'''
    Takes dictionary of just section ['General settings'] and the path of the .ini driver
    Returns dictionary with all keys and values (given and default) as defined by section 12.1.2 in Labber manual
'''
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

'''
    Takes dictionary of just section ['Models and options'] 
    Returns dictionary with all keys and values (given and default) as defined by section 12.1.3 in Labber manual
'''
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
    
    models = {model_strs[i]: model_ids[i] for i in range(len(model_strs))}

    if 'check_options' in settings:
        check_options = settings['check_options']
    else:
        check_options = None

    if 'option_cmd' in settings:
        option_cmd = settings['option_cmd']
    else:
        option_cmd = None

    # gets all values for any key containing key 'option_str_'
    option_strs = [value for key, value in settings.items() if 'option_str_' in key]

    # gets all values for any key containing key 'option_id_'
    option_ids = [value for key, value in settings.items() if 'option_id_' in key]

    # number of option_strs and option_ids must match unless no option_ids are provided
    if len(option_ids) != 0 and len(option_ids) != len(option_strs):
        raise ValueError(
            "Number of option_strs provided does not match number of option_ids provided in ['Model and options']")

    # if no option_ids are provided, option_strs used instead
    if len(option_ids) == 0:
        option_ids = option_strs

    options = {option_strs[i]: option_ids[i] for i in range(len(option_strs))}

    return {
        'check_model': check_model,
        'model_cmd': model_cmd,
        'models': models,
        'check_options': check_options,
        'option_cmd': option_cmd,
        'options': options
    }

'''
    Takes dictionary of just section ['VISA settings']
    Returns dictionary with all keys and values (given and default) as defined by section 12.1.4 in Labber manual
'''
def getVISASettings(settings: dict) -> dict:
    if 'use_visa' in settings:
        use_visa = bool(settings['use_visa'])
    else:
        use_visa = None

    if 'reset' in settings:
        reset = bool(settings['reset'])
    else:
        reset = False

    if 'query_instr_errors' in settings:
        query_instr_errors = bool(settings['query_instr_errors'])
    else:
        query_instr_errors = False

    if 'error_bit_mask' in settings:
        error_bit_mask = int(settings['error_bit_mask'])
    else:
        error_bit_mask = 255

    if 'init' in settings:
        init = settings['init']
    else:
        init = None

    if 'final' in settings:
        final = settings['final']
    else:
        final = None

    if 'str_true' in settings:
        str_true = settings['str_true']
    else:
        str_true = '1'

    if 'str_false' in settings:
        str_false = settings['str_false']
    else:
        str_false = '0'

    if 'str_value_out' in settings:
        str_value_out = settings['str_value_out']
    else:
        str_value_out = '%.9e'

    if 'str_value_strip_start' in settings:
        str_value_strip_start = int(settings['str_value_strip_start'])
    else:
        str_value_strip_start = 0

    if 'str_value_strip_end' in settings:
        str_value_strip_end = int(settings['str_value_strip_end'])
    else:
        str_value_strip_end = 0

    if 'always_read_after_write' in settings:
        always_read_after_write = bool(settings['always_read_after_write'])
    else:
        always_read_after_write = False

    if 'timeout' in settings:
        timeout = int(settings['timeout'])
    else:
        timeout = 5

    if 'term_char' in settings:
        term_char = settings['term_char']
        if term_char not in ('AUTO', 'NONE', 'CR', 'LF', 'CR+LF'):
            raise ValueError(f"Invalid value '{term_char}' for [VISA settings].term_char")
    else:
        term_char = None

    if 'send_end_on_write' in settings:
        send_end_on_write = bool(settings['send_end_on_write'])
    else:
        send_end_on_write = None

    if 'suppress_end_on_read' in settings:
        suppress_end_on_read = bool(settings['suppress_end_on_read'])
    else:
        suppress_end_on_read = None

    if 'baud_rate' in settings:
        baud_rate = int(settings['baud_rate'])
    else:
        baud_rate = 9600

    if 'data_bits' in settings:
        data_bits = int(settings['data_bits'])
    else:
        data_bits = 8

    if 'stop_bits' in settings:
        stop_bits = float(settings['stop_bits'])
        if stop_bits not in (1, 1.5, 2):
            raise ValueError(f"Invalid value '{stop_bits}' for [VISA settings].stop_bits")
    else:
        stop_bits = 1

    if 'parity' in settings:
        parity = str.upper(settings['stop_bits'])
        if parity not in ('NO PARITY', 'ODD PARITY', 'EVEN PARITY'):
            raise ValueError(f"Invalid value '{parity}' for [VISA settings].parity")
    else:
        parity = None

    if 'gpib_board' in settings:
        gpib_board = int(settings['gpib_board'])
    else:
        gpib_board = 8

    if 'gpib_go_to_local' in settings:
        gpib_go_to_local = bool(settings['gpib_go_to_local'])
    else:
        gpib_go_to_local = False

    if 'tcpip_specify_port' in settings:
        tcpip_specify_port = bool(settings['tcpip_specify_port'])
    else:
        tcpip_specify_port = False

    if 'tcpip_port' in settings:
        tcpip_port = settings['tcpip_port']
    else:
        tcpip_port = None

    if tcpip_specify_port and not (tcpip_port is None or not tcpip_port):
        raise ValueError(f'[VISA settings].tcpip_port must be specified when [VISA settings].tcpip_specify_port is true')

    return {
        'use_visa': use_visa,
        'reset': reset,
        'query_instr_errors': query_instr_errors,
        'error_bit_mask': error_bit_mask,
        'init': init,
        'final': final,
        'str_true': str_true,
        'str_false': str_false,
        'str_value_out': str_value_out,
        'str_value_strip_start': str_value_strip_start,
        'str_value_strip_end': str_value_strip_end,
        'always_read_after_write': always_read_after_write,
        'timeout': timeout,
        'term_char': term_char,
        'send_end_on_write': send_end_on_write,
        'suppress_end_on_read': suppress_end_on_read,
        'baud_rate': baud_rate,
        'data_bits': data_bits,
        'stop_bits': stop_bits,
        'parity': parity,
        'gpib_board': gpib_board,
        'gpib_go_to_local': gpib_go_to_local,
        'tcpip_specify_port': tcpip_specify_port,
    }

'''
    Takes dictionary of all sections excluding ['General settings'], ['Models and options'], ['VISA settings']
    Returns dictionary of dictionaries where each nested dictionary are
        the quantities with all keys and values (given and default) as defined by section 12.2 in Labber manual
'''
def getQuantities(settings: dict) -> dict:
    quantities = {}
    for key in settings:
        quantity = settings[key]

        if 'label' in quantity:
            label = quantity['label']
        else:
            label = key

        if 'datatype' in quantity:
            datatype = str.upper(quantity['datatype'])
            if datatype not in \
                    ('DOUBLE', 'BOOLEAN', 'COMBO', 'STRING', 'COMPLEX', 'VECTOR', 'VECTOR_COMPLEX', 'PATH', 'BUTTON'):
                raise ValueError(f'Invlaid value {datatype} for [{key}].datatype')
        else:
            raise ValueError(f"Expected 'datatype' for qunatity [{key}]")

        if 'unit' in quantity:
            unit = quantity['unit']
        else:
            unit = None

        if 'def_value' in quantity:
            def_value = quantity['def_value']
        else:
            def_value = None

        if 'tooltip' in quantity:
            tooltip = quantity['tooltip']
        else:
            tooltip = None

        if 'low_lim' in quantity:
            low_lim = quantity['low_lim']
        else:
            low_lim = '-INF'

        if 'high_lim' in quantity:
            high_lim = quantity['high_lim']
        else:
            high_lim = '+INF'

        # x_name is only valid for vectors
        if 'x_name' in quantity and datatype in ('VECTOR', 'VECTOR_COMPLEX'):
            x_name = quantity['x_name']
        else:
            x_name = None

        # x_unit is only valid for vectors
        if 'x_unit' in quantity and datatype in ('VECTOR', 'VECTOR_COMPLEX'):
            x_unit = quantity['x_unit']
        else:
            x_unit = None

        # combo data type must have 'combo_def's in quantity
        combos = [value for key, value in quantity.items() if 'combo_def_' in key]
        if datatype == 'COMBO':
            if len(combos) == 0:
                raise ValueError(f"Quantity [{key}] must contain at least 'combo_def_1' if datatype is 'COMBO'")
        else:
            combos = None

        if 'group' in quantity:
            group = quantity['group']
        else:
            group = None

        if 'section' in quantity:
            section = quantity['section']
        else:
            section = None

        if 'state_quant' in quantity:
            state_quant = quantity['state_quant']
        else:
            state_quant = None

        ''' 
        States, values, and options can have multiple entries such as state_value_1, state_value2,..., state_value_n
        The following lines grab all keys and values with the given patterns and make a list of the values
        '''
        state_values = [value for key, value in quantity.items() if 'state_value_' in key]
        model_values = [value for key, value in quantity.items() if 'model_value_' in key]
        option_values = [value for key, value in quantity.items() if 'option_value_' in key]

        if 'permission' in quantity:
            permission = str.upper(quantity['permission'])
            if permission not in ('BOTH', 'READ', 'WRITE', 'NONE'):
                raise ValueError(f"Invalid value '{permission}' for [{key}].permission")
        else:
            permission = 'BOTH'

        if 'show_in_measurement_dlg' in quantity:
            show_in_measurement_dlg = bool(quantity['show_in_measurement_dlg'])
        else:
            show_in_measurement_dlg = None

        if 'set_cmd' in quantity:
            set_cmd = quantity['set_cmd']
        else:
            set_cmd = None

        if 'get_cmd' in quantity:
            get_cmd = quantity['get_cmd']
        else:
            get_cmd = 'get_cmd?'

        # combo data type must have 'combo_def's in quantity
        cmds = [value for key, value in quantity.items() if 'cmd_def_' in key]
        if datatype == 'COMBO':
            if len(cmds) == 0:
                raise ValueError(f"Quantity [{key}] must contain at least 'cmd_def_1' if datatype is 'COMBO'")
        else:
            cmds = None

        # id datatype is 'COMBO' must have same number of combo_defs and cmd_defs
        # turn combos and cmds into dictionary
        if combos and cmds:
            if len(combos) != len(cmds):
                raise ValueError(f"Quantity [{key}] must contain the same number of 'combo_def' and 'cmd_def' if datatype is 'COMBO'")
            else:
                combo_cmd = {combos[i]: cmds[i] for i in range(len(combos))}

        quantities[label] = {
            'label': label,
            'data_type': datatype,
            'unit': unit,
            'def_value': def_value,
            'tool_tip': tooltip,
            'low_lim': low_lim,
            'high_lim': high_lim,
            'x_name': x_name,
            'x_unit': x_unit,
            'groupname': group,
            'section': section,
            'state_quant': state_quant,
            'state_values': state_values,
            'model_values': model_values,
            'option_values': option_values,
            'permission': permission,
            'show_in_measurement_dlg': show_in_measurement_dlg,
            'set_cmd': set_cmd,
            'get_cmd': get_cmd,
            #'combo_cmd': combo_cmd
        }
    
    return quantities