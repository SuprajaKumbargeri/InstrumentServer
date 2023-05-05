import flask_instrument_server

""" 
This is the main "entry point" that starts Instrument Server and
the associated QT applications.
"""


def main():
    """
    Creates & Deploys Instrument Server
    Add dev_mode=True to NOT load a VISA backend (required to connect to instruments).
    """
    server = flask_instrument_server.FlaskInstrumentServer(dev_mode=True)
    server.run_server()


if __name__ == "__main__":
    main()
