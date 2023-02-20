###################################################################################
# Blueprint: 'instrumentCom'
###################################################################################

import logging
import re
from flask import (Blueprint, jsonify, request)
from werkzeug.exceptions import abort
from .. InstrumentDetection.instrument_resource import *
from . import instrument_com_service as ics

'''
Create 'instrumentCom' Blueprint
'''
bp = Blueprint('instrumentCom', __name__,  url_prefix='/instrumentCom')


def initialize(logger: logging.Logger):
    global my_logger 
    my_logger = logger

    global inst_com_serv 
    inst_com_serv = ics.InstrumentComService(my_logger)


@bp.route('/')
def index():
    my_logger.info("/instrumentCom was hit!")
    return jsonify("This is the /instrumentCom endpoint"), 200


@bp.route('/closeAllInstruments/', methods=['GET'])
def closeAllInstruments():
    inst_com_serv.close_all_instruments()
    return jsonify("All Instruments are closed!"), 200

    
@bp.route('/ask/', methods=['GET'])
def ask():
    # Get the provided content as json
    content = request.json

    inst = content['Instrumnet']
    interface = content['Interface']
    type = content['Type']
    cmd = content['Command']

    inst_resp = inst_com_serv.handle_ask(instrument=inst, cmd=cmd, type=INST_TYPE.VISA)

    if (inst_resp == 404):
        resp = jsonify("Instrument {0} is not detected".format(inst)), 404
    elif (inst_resp == 500):
        resp = jsonify("INTERNAL SERVER ERROR"), 500
    else:
        resp = jsonify(inst_resp), 200
        
    return resp
