###################################################################################
# Blueprint: 'serverStatus'
###################################################################################

import platform
import logging
import datetime
import sys

from flask import (Blueprint, jsonify)
from werkzeug.exceptions import abort

'''
Create 'serverStatus' Blueprint
'''
bp = Blueprint('serverStatus', __name__,  url_prefix='/serverStatus')


def set_Logger(logger: logging.Logger):
    global my_logger 
    my_logger = logger


@bp.route('/healthCheck')
def health_check():
    my_logger.debug("/healthCheck was hit!")
    return jsonify("Instument Server is running!"), 200


@bp.route('/')
def index():
    my_logger.debug("/serverStatus was hit!")
    return jsonify("This is the /status endpoint"), 200


@bp.route('/getOsPlatform')
def get_Os_Platform():
    my_logger.debug("/getOsPlatform was hit!")
    return jsonify(platform.system()), 200


@bp.route('/getServerUTCTime')
def get_server_utc_time():
    my_logger.debug("/getServerUTCTime was hit!")
    return jsonify(datetime.datetime.utcnow()), 200
