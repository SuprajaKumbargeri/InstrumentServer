import json
from psycopg2.extensions import AsIs
import logging
from flask import request, current_app, g
from flask import Blueprint, jsonify
from werkzeug.exceptions import (abort, BadRequestKeyError)

import db, instrumentDBService as ids
import driverParser as dp


bp = Blueprint("instrumentDB", __name__,  url_prefix='/instrumentDB')

def setLogger(logger: logging.Logger):
    global my_logger 
    my_logger = logger

''' Adds instrument details to the database '''
@bp.route('/addInstrument')
def addInstrument():
    try:        
        global instrument_details
        result = json.loads(request.args['details'])
        details = result['details']
        instrument_details = dp.addDriver(details['path'])[0]
        connection = db.get_db()
        cute_name = details['cute_name']
        manufacturer = instrument_details['general_settings']['name']

        ids.addInstrumentInterface(connection, details, manufacturer)
        ids.addGenSettings(connection, instrument_details['general_settings'], cute_name)
        ids.addModelOptions(connection, instrument_details['model_and_options'], cute_name)
        ids.addVisaSettings(connection, instrument_details['visa'], cute_name)
        for quantity in instrument_details['quantities'].keys():
            ids.addQuantity(connection, instrument_details['quantities'][quantity], cute_name)
        connection.commit()

        db.close_db(connection)
        return jsonify("Instrument added."), 200

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400


''' Returns 'cute_name' and 'manufacturer' of existing instruments '''
@bp.route('/allInstruments')
def allInstruments():
    try:
        connection = db.get_db()
        all_instruments = {}

        with connection.cursor() as cursor:
            all_instruments_query = "SELECT cute_name, manufacturer, interface, ip_address FROM {table_name};".format(table_name="instruments")           
            cursor.execute(all_instruments_query)
            result = cursor.fetchall()

            for instrument in result:
                all_instruments[instrument[0]] = {'manufacturer': instrument[1], 'interface': instrument[2], 'ip_address': instrument[3]}

        db.close_db(connection)
        if len(all_instruments) == 0:
            return jsonify("No instruments were added."), 200
        return jsonify(all_instruments), 200

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400


@bp.route('/getInstrument')
def getInstruments():
    try:
        instrument_name = request.args['cute_name']        
        connection = db.get_db()
        instrument_interface = ids.getInstrumentInterface(connection, instrument_name)
        general_settings = ids.getGenSettings(connection, instrument_name)
        model_options = ids.getModelOptions(connection, instrument_name)
        visa_settings = ids.getVisaSettings(connection, instrument_name)
        quantities = ids.getQuantities(connection, instrument_name)




        return jsonify({'instrument_interface' : instrument_interface, 'general_settings' : general_settings, 'model_and_options' : model_options, 'visa' : visa_settings, 'quantities' : quantities}), 200

    except IndexError:
        my_logger.error('Invalid instrument name.')
        return jsonify('Invalid instrument name.'), 400

    except BadRequestKeyError:
        my_logger.error('No instrument name was given.')
        return jsonify('No instrument name was given.'), 400

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400


''' Returns latest value of label '''
@bp.route('/getLatestValue')
def getLatestValue():
    try:
        instrument_name = request.args['cute_name']
        label = request.args['label']
        connection = db.get_db()
        latest_value = ids.getLatestValue(connection, instrument_name, label)
        db.close_db(connection)
        return jsonify({'latest_value': latest_value}), 200

    except BadRequestKeyError:
        my_logger.error('Invalid instrument name.')
        return jsonify('Invalid instrument name.'), 400

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400


''' Set latest value of label '''
@bp.route('/setLatestValue')
def setLatestValue():
    try:
        instrument_name = request.args['cute_name']
        label = request.args['label']
        latest_value = request.args['latest_value']
        connection = db.get_db()
        ids.setLatestValue(connection, latest_value, instrument_name, label)
        db.close_db(connection)
        return jsonify("Instrument's latest value on {label} updated.".format(label=label)), 200

    except BadRequestKeyError:
        my_logger.error('Invalid instrument name or label.')
        return jsonify('Invalid instrument name or label.'), 400

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400