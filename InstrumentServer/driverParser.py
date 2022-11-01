import json
from msilib.schema import Error
import platform
import logging
from flask import request
from configparser import ConfigParser

from flask import (Blueprint, jsonify)
from werkzeug.exceptions import (abort, BadRequestKeyError)

bp = Blueprint("driverParser", __name__,  url_prefix='/driverParser')
driver = None
config = ConfigParser()


def setLogger(logger: logging.Logger):
    global my_logger 
    my_logger = logger


'''Parses driver from a given local path. Returns dictionary of the driver contents'''
@bp.route('/')
def parseDriver():
    my_logger.debug("parseDriver was hit")

    try:
        # driver = request.args['driverPath']
        global driver
        driver = 'C:\\Users\\thoma\\PycharmProjects\\algohw3\\RohdeSchwarz_SGS100.ini'

        config.read(driver)
        return jsonify(config._sections), 200

    except BadRequestKeyError:
        my_logger.error('parseDriver: No path to driver was given.')
        return jsonify('No path to driver was given.'), 400
    except Exception:
        my_logger.error(Exception.args)
        return jsonify(Exception.args), 400


@bp.route('/<setting>')
@bp.route('/<setting>/<field>')
def getSettings(setting, field=None):
    my_logger.debug("parseDriver/getSettings was hit")
    
    if driver is None:
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
