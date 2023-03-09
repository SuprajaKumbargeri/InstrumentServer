import flask_instrument_server


def main():
    """Creates & Deploys Instrument Server"""
    server = flask_instrument_server.FlaskInstrumentServer()
    server.run_server()


if __name__ == "__main__":
    main()
