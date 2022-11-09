def getGenSettings(settings: dict, ini_path) -> dict:
    if 'driver_path' in settings:
        driver_path = settings['driver_path']
    else:
        driver_path = None

    if 'interface' in settings:
        interface = settings['interface']
    else:
        interface = 'GPIB'

    if 'address' in settings:
        address = settings['address']
    else:
        address = None

    if 'startup' in settings:
        startup = settings['startup']
    else:
        startup = 'Set config'

    if 'signal_generator' in settings:
        is_signal_generator = bool(settings['signal_generator'])
    else:
        is_signal_generator = False

    if 'signal_analyzer' in settings:
        is_signal_analyzer = bool(settings['signal_analyzer'])
    else:
        is_signal_analyzer = False

    if 'controller' in settings:
        is_controller = bool(settings['controller'])
    else:
        is_controller = False

    return {
        'name': settings['name'],
        'ini_path': ini_path,
        'driver_path': driver_path,
        'interface': interface,
        'address': address,
        'startup': startup,
        'is_signal_generator': is_signal_generator,
        'is_signal_analyzer': is_signal_analyzer,
        'is_controller': is_controller
    }


def getModelOptions(settings: dict) -> dict:
    if 'check_model' in settings:
        check_model = bool(settings['check_model'])
    else:
        check_model = False

    if 'model_cmd' in settings:
        model_cmd = settings['model_cmd']
    else:
        model_cmd = '*IDN?'

    # gets all values for any key containing key 'model_str_'
    model_strs = [value for key, value in settings.items() if 'model_str_' in key]

    # gets all values for any key containing key 'model_id_'
    model_ids = [value for key, value in settings.items() if 'model_id_' in key]

    # number of model_strs and model_ids must match unless no model_ids are provided
    if len(model_ids) != 0 and len(model_ids) != len(model_strs):
        raise ValueError("Number of model_strs provided does not match number of model_ids provided in ['Model and options']")

    # if no model_ids are provided, model_strs used instead
    if len(model_ids) == 0:
        model_ids = model_strs

    if 'check_options' in settings:
        check_model = settings['check_options']
    else:
        check_options = None

    if 'option_cmd' in settings:
        option_cmd = settings['option_cmd']
    else:
        option_cmd = None

    # gets all values for any key containing key 'option_str_'
    option_strs = [value for key, value in settings.items() if 'otion_str_' in key]

    # gets all values for any key containing key 'option_id_'
    option_ids = [value for key, value in settings.items() if 'option_id_' in key]

    # number of option_strs and option_ids must match unless no option_ids are provided
    if len(option_ids) != 0 and len(option_ids) != len(option_strs):
        raise ValueError(
            "Number of option_strs provided does not match number of option_ids provided in ['Model and options']")

    # if no option_ids are provided, option_strs used instead
    if len(option_ids) == 0:
        option_ids = option_strs

    return {
        'check_model': check_model,
        'model_cmd': model_cmd,
        'models': {model_strs[i]: model_ids[i] for i in range(len(model_strs))},
        'check_options': check_options,
        'option_cmd': option_cmd,
        'options': {option_strs[i]: option_ids[i] for i in range(len(option_strs))}
    }