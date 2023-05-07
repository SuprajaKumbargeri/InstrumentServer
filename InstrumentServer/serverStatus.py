###################################################################################
# Blueprint: 'serverStatus'
###################################################################################

import platform
import logging
import datetime
from http import HTTPStatus

from flask import (Blueprint, jsonify)

'''
Create 'serverStatus' Blueprint
'''
bp = Blueprint('serverStatus', __name__,  url_prefix='/serverStatus')


def set_logger(logger: logging.Logger):
    global my_logger 
    my_logger = logger


@bp.route('/isRunning')
def health_check():
    my_logger.debug("/isRunning was hit!")
    return jsonify("Instrument Server is running!"), HTTPStatus.OK


@bp.route('/')
def index():
    my_logger.debug("/serverStatus was hit!")
    return jsonify("This is the /serverStatus endpoint"), HTTPStatus.OK


@bp.route('/getOsPlatform')
def get_Os_Platform():
    my_logger.debug("/getOsPlatform was hit!")
    return jsonify(platform.system()), HTTPStatus.OK


@bp.route('/getServerUTCTime')
def get_server_utc_time():
    my_logger.debug("/getServerUTCTime was hit!")
    return jsonify(datetime.datetime.utcnow()), HTTPStatus.OK
