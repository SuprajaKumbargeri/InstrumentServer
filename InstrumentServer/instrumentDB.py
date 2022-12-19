import json
from psycopg2.extensions import AsIs
import logging
from flask import request, current_app, g
from flask import Blueprint, jsonify
from werkzeug.exceptions import (abort, BadRequestKeyError)

from . import db, instrumentDBService as ids


bp = Blueprint("instrumentDB", __name__,  url_prefix='/instrumentDB')

def setLogger(logger: logging.Logger):
    global my_logger 
    my_logger = logger


''' Adds instrument details to the database '''
@bp.route('/addInstrument')
def addInstrument():
    try:        
        global instrument_details
        instrument_details = json.loads(request.args['details'])
        
        connection = db.get_db()        
        id = ids.addGenSettings(connection, instrument_details['general_settings'])
        ids.addModelOptions(connection, instrument_details['model_and_options'], id)        
        ids.addVisaSettings(connection, instrument_details['visa'], id)
        for quantity in instrument_details['quantities'].keys():
            ids.addQuantity(connection, instrument_details['quantities'][quantity], id)

        connection.commit()
        db.close_db(connection)
        return jsonify("Instrument added."), 200

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400


''' Returns 'id' and 'name' of existing instruments '''
@bp.route('/allInstruments')
def allInstruments():
    try:
        connection = db.get_db()
        all_instruments = {}

        with connection.cursor() as cursor:
            all_instruments_query = "SELECT id, name FROM {table_name};".format(table_name="general_settings")            
            cursor.execute(all_instruments_query)
            result = cursor.fetchall()

            for instrument in result:
                all_instruments[instrument[0]] = instrument[1]

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
        instrument_id = request.args['id']        
        connection = db.get_db()
        general_settings = ids.getGenSettings(connection, instrument_id)
        model_options = ids.getModelOptions(connection, instrument_id)
        visa_settings = ids.getVisaSettings(connection, instrument_id)
        quantities = ids.getQuantities(connection, instrument_id)
        

        

        return jsonify({'general_settings' : general_settings, 'model_and_options' : model_options, 'visa' : visa_settings, 'quantities' : quantities}), 200

    except IndexError:
        my_logger.error('Invalid instrument id.')
        return jsonify('Invalid instrument id.'), 400

    except BadRequestKeyError:
        my_logger.error('No instrument id was given.')
        return jsonify('No instrument id was given.'), 400

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400