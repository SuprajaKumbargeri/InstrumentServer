import psycopg2
import logging
from flask import current_app, g

def setLogger(logger: logging.Logger):
    global my_logger 
    my_logger = logger

def get_db():    
    connection = psycopg2.connect(current_app.config['DATABASE'])
    my_logger.debug("db connection established!")
    return connection

def close_db(connection):
    if connection:
        connection.close()

def init_db(app):
    with app.app_context():
        
        connection = get_db()
        cursor = connection.cursor()
        
        with current_app.open_resource('schema.sql', mode='r') as f:
            cursor.execute(f.read())

        cursor.close()
        connection.commit()
        my_logger.debug("db is initialised!")     