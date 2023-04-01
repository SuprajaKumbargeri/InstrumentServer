import flask_instrument_server


def main():
    """Creates & Deploys Instrument Server
    Add dev_mode=True to NOT load VISA backend
    """
    server = flask_instrument_server.FlaskInstrumentServer()
    server.run_server()


if __name__ == "__main__":
    main()
