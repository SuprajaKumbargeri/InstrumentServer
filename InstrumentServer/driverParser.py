import json
from msilib.schema import Error
import platform
import logging
from flask import request, redirect, url_for
from configparser import ConfigParser
from flask import (Blueprint, jsonify)
from werkzeug.exceptions import (abort, BadRequestKeyError)

from . import driverParserService as dps

bp = Blueprint("driverParser", __name__,  url_prefix='/driverParser')
ini_path = None
config = ConfigParser()


def setLogger(logger: logging.Logger):
    global my_logger 
    my_logger = logger


'''Parses driver from a given local path. Returns dictionary of the driver contents'''
@bp.route('/')
def parseDriver():
    try:
        global ini_path
        ini_path = request.form['driverPath']

        config.read(ini_path)
        gen_settings = dps.getGenSettings(dict(config['General settings']), ini_path)
        model_options = dps.getModelOptions(dict(config['Model and options']))
        visa_settings = dps.getVISASettings(dict(config['VISA settings']))
        quantities = dps.getQuantities({key: value for key, value in config._sections.items() \
                                        if key not in ('General settings', 'Model and options', 'VISA settings')})
        return jsonify({'general_settings': gen_settings, 'model_and_options': model_options, 'visa': visa_settings,
                        'quantities': quantities}), 200

    except Exception as e:
        my_logger.error(e.args)
        return jsonify(e.args), 400


@bp.route('/addDriver')
def addDriver():
    try:
        global ini_path
        ini_path = request.form['driverPath']
        
        config.read(ini_path)
        gen_settings = dps.getGenSettings(dict(config['General settings']), ini_path)
        model_options = dps.getModelOptions(dict(config['Model and options']))
        visa_settings = dps.getVISASettings(dict(config['VISA settings']))
        quantities = dps.getQuantities({key: value for key, value in config._sections.items()\
                if key not in ('General settings', 'Model and options', 'VISA settings')})
        return redirect(url_for('instrumentDB.addInstrument', details = json.dumps({'general_settings': gen_settings, 
        'model_and_options': model_options, 'visa': visa_settings, 'quantities': quantities})))

    except Exception as e:
        my_logger.error(e.args)
        return jsonify(e.args), 400


@bp.route('/<setting>')
@bp.route('/<setting>/<field>')
def getSettings(setting, field=None):
    my_logger.debug("parseDriver/getSettings was hit")
    
    if ini_path is None:
        my_logger.error('parseDriver/getSettings: No path to driver was given.')
        return jsonify('No path to driver was given.'), 400

    try:
        if field is None:
            return jsonify(dict(config[setting])), 200
        else:
            return jsonify(config[setting][field]), 200

    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400
