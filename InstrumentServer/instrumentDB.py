import logging
from flask import request
from psycopg2 import errors
import requests
from flask import Blueprint, jsonify
from werkzeug.exceptions import (BadRequestKeyError)
import instrumentDBService as ids
from DB import db
from http import HTTPStatus

bp = Blueprint("instrumentDB", __name__,  url_prefix='/instrumentDB')
UniqueViolation = errors.lookup('23505')

def setLogger(logger: logging.Logger):
    global my_logger 
    my_logger = logger

''' Adds instrument details to the database '''
@bp.route('/addInstrument', methods=['GET', 'POST'])
def addInstrument():
    try:        
        details = request.get_json()
        url = r'http://127.0.0.1:5000/driverParser/'
        instrument_details = requests.post(url, json=details['path'])
        if HTTPStatus.MULTIPLE_CHOICES > instrument_details.status_code <= HTTPStatus.OK:
            connection = db.get_db()
            cute_name = details['cute_name']
            instrument_details = instrument_details.json()
            manufacturer = instrument_details['general_settings']['name']
            
            ids.addInstrumentInterface(connection, details, manufacturer)
            ids.addGenSettings(connection, instrument_details['general_settings'], cute_name)
            ids.addModelOptions(connection, instrument_details['model_and_options'], cute_name)
            ids.addVisaSettings(connection, instrument_details['visa'], cute_name)
            for quantity in instrument_details['quantities'].keys():
                ids.addQuantity(connection, instrument_details['quantities'][quantity], cute_name)
            connection.commit()

            # If the baud rate is provided, we will overwrite the value we got from the ini file
            if details['baud_rate']:
                my_logger.info(f"Baud Rate: {details['baud_rate']} was provided. Replacing value from ini file.")
                ids.update_visa_baud_rate(connection, cute_name, details['baud_rate'])

            db.close_db(connection)
            return jsonify(f"Instrument: \"{details['cute_name']}\" was (re)added!"), HTTPStatus.OK
        else:
            raise FileNotFoundError
        
    except FileNotFoundError:
        my_logger.error("Invalid driver path.")
        return jsonify("Invalid driver path."), HTTPStatus.BAD_REQUEST
    
    except UniqueViolation:
        connection.rollback()
        db.close_db(connection)
        my_logger.error("Instrument name already exists.")
        return jsonify("Instrument name already exists."), HTTPStatus.BAD_REQUEST

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), HTTPStatus.BAD_REQUEST


''' Returns 'cute_name' and 'manufacturer' of existing instruments '''
@bp.route('/allInstruments')
def allInstruments():
    try:
        connection = db.get_db()
        all_instruments = {}

        with connection.cursor() as cursor:
            all_instruments_query = "SELECT cute_name, manufacturer, interface, address FROM {table_name};".format(table_name="instruments")
            cursor.execute(all_instruments_query)
            result = cursor.fetchall()

            for instrument in result:
                all_instruments[instrument[0]] = {'manufacturer': instrument[1], 'interface': instrument[2], 'address': instrument[3]}

        db.close_db(connection)
        if len(all_instruments) == 0:
            return jsonify("No instruments were added."), HTTPStatus.OK
        return jsonify(all_instruments), HTTPStatus.OK

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), HTTPStatus.BAD_REQUEST


@bp.route('/getInstrument')
def getInstrument():
    try:
        instrument_name = request.args['cute_name']        
        connection = db.get_db()
        instrument_interface = ids.getInstrumentInterface(connection, instrument_name)
        general_settings = ids.getGenSettings(connection, instrument_name)
        model_options = ids.getModelOptions(connection, instrument_name)
        visa_settings = ids.getVisaSettings(connection, instrument_name)
        quantities = ids.getQuantities(connection, instrument_name)

        db.close_db(connection)
        return jsonify({'instrument_interface' : instrument_interface, 'general_settings' : general_settings, 'model_and_options' : model_options, 'visa' : visa_settings, 'quantities' : quantities}), HTTPStatus.OK

    except BadRequestKeyError:
        my_logger.error('Invalid instrument name.')
        return jsonify('Invalid instrument name.'), HTTPStatus.BAD_REQUEST

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), HTTPStatus.BAD_REQUEST

@bp.route('/getInstrumentSettings', methods = ['GET'])
def getInstrumentSettings():
    try:
        instrument_name = request.args['cute_name']
        connection = db.get_db()
        instrument_interface = ids.getInstrumentInterface(connection, instrument_name)
        general_settings = ids.getGenSettings(connection, instrument_name)
        visa_settings = ids.getVisaSettings(connection, instrument_name)

        db.close_db(connection)
        return jsonify({'instrument_interface' : instrument_interface, 'general_settings' : general_settings, 'visa' : visa_settings}), HTTPStatus.OK

    except BadRequestKeyError:
        my_logger.error('Invalid instrument name.')
        return jsonify('Invalid instrument name.'), HTTPStatus.BAD_REQUEST

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), HTTPStatus.BAD_REQUEST


''' Returns latest value of label '''
@bp.route('/getLatestValue')
def getLatestValue():
    try:
        instrument_name = request.args['cute_name']
        label = request.args['label']
        connection = db.get_db()
        latest_value = ids.getLatestValue(connection, instrument_name, label)
        db.close_db(connection)
        return jsonify({'latest_value': latest_value}), HTTPStatus.OK

    except BadRequestKeyError:
        my_logger.error('Invalid instrument name.')
        return jsonify('Invalid instrument name.'), HTTPStatus.BAD_REQUEST

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), HTTPStatus.BAD_REQUEST



''' Set latest value of label '''
@bp.route('/setLatestValue', methods = ['PUT'])
def setLatestValue():
    try:
        instrument_name = request.args['cute_name']
        label = request.args['label']
        latest_value = request.args['latest_value']
        connection = db.get_db()
        ids.setLatestValue(connection, latest_value, instrument_name, label)
        db.close_db(connection)
        return jsonify("Instrument's latest value on {label} updated.".format(label=label)), HTTPStatus.OK

    except BadRequestKeyError:
        my_logger.error('Invalid instrument name or label.')
        return jsonify('Invalid instrument name or label.'), HTTPStatus.BAD_REQUEST

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), HTTPStatus.BAD_REQUEST
    
@bp.route('/removeInstrument')
def removeInstrument():
    try:
        instrument_name = request.args['cute_name']        
        connection = db.get_db()
        ids.deleteInstrument(connection, instrument_name)
        db.close_db(connection)
        return jsonify('Instrument removed.'), HTTPStatus.OK
    
    except BadRequestKeyError:
        my_logger.error('Invalid instrument name.')
        return jsonify('Invalid instrument name.'), HTTPStatus.BAD_REQUEST
    
    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), HTTPStatus.BAD_REQUEST