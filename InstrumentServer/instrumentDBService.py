import psycopg2
from psycopg2.extensions import AsIs

def addInstrumentInterface(connection, ins_interface: dict, manufacturer):

    table = 'instruments'
    with connection.cursor() as cursor:

        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)           
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        columns, values = [], []

        for column_name in column_names:
            if column_name[0] in ins_interface.keys():
                if ins_interface[column_name[0]]:
                    columns.append(column_name[0])
                    values.append(ins_interface[column_name[0]])

        columns.append('manufacturer')
        values.append(manufacturer) 

        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))
        cursor.execute(insert_statement)


def addGenSettings(connection, gen_settings: dict, cute_name):
 
    table = 'general_settings'

    with connection.cursor() as cursor:

        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)           
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        columns, values = [], []

        for column_name in column_names:
            if column_name[0] in gen_settings.keys():
                if gen_settings[column_name[0]]:
                    columns.append(column_name[0])
                    values.append(gen_settings[column_name[0]])
       
        columns.append('cute_name')
        values.append(cute_name)        
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))
        cursor.execute(insert_statement)


def addModelOptions(connection, model_options: dict, cute_name):

    table = 'model_and_options'
    with connection.cursor() as cursor:

        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)           
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        columns, values = [], []

        for column_name in column_names:
            if column_name[0] in model_options.keys():
                if column_name[0] == 'models':
                    columns.append('models')
                    models = '{' + ','.join(model_options['models'].keys()) + '}'
                    values.append(models)
                    columns.append('model_ids')
                    model_ids = '{' + ','.join(model_options['models'].values()) + '}'
                    values.append(model_ids)
                elif column_name[0] == 'options':
                    columns.append('options')
                    options = '{' + ','.join(model_options['options'].keys()) + '}'
                    values.append(options)
                    columns.append('option_ids')
                    option_ids = '{' + ','.join(model_options['options'].values()) + '}'
                    values.append(option_ids)
                elif model_options[column_name[0]]:
                    columns.append(column_name[0])
                    values.append(model_options[column_name[0]])

        columns.append('cute_name')
        values.append(cute_name)         
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))
        cursor.execute(insert_statement)


def addVisaSettings(connection, visa_settings: dict, cute_name):

    table = 'visa'
    with connection.cursor() as cursor:

        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)           
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        columns, values = [], []

        for column_name in column_names:
            if column_name[0] in visa_settings.keys():
                if visa_settings[column_name[0]]:
                    columns.append(column_name[0])
                    values.append(visa_settings[column_name[0]])

        columns.append('cute_name')
        values.append(cute_name)         
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))
        cursor.execute(insert_statement)

def addQuantity(connection, quantity: dict, cute_name):

    table = 'quantities'
    with connection.cursor() as cursor:

        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)           
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        columns, values = [], []        

        for column_name in column_names:
            if column_name[0] in quantity.keys():             
                if column_name[0] == 'state_values':
                    columns.append('state_values')
                    state_values = '{' + ','.join(quantity['state_values']) + '}'
                    values.append(state_values)
                
                elif column_name[0] == 'model_values':
                    columns.append('model_values')
                    model_values = '{' + ','.join(quantity['model_values']) + '}'
                    values.append(model_values)
                    
                elif column_name[0] == 'option_values':
                    columns.append('option_values')
                    option_values = '{' + ','.join(quantity['option_values']) + '}'
                    values.append(option_values)                    

                elif quantity[column_name[0]]:
                    columns.append(column_name[0])
                    values.append(quantity[column_name[0]])

        columns.append('cute_name')
        values.append(cute_name)         
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))        
        cursor.execute(insert_statement)

def getInstrumentInterface(connection: object, instrument_name: str) -> dict:

    table = 'instruments'
    general_settings = {}
    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)
        
        get_instrument_query = cursor.mogrify("SELECT %s FROM %s WHERE cute_name = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_name))
        cursor.execute(get_instrument_query)
        result = cursor.fetchmany()
        ins_interface = {key : value for key, value in zip(column_names, result[0])}

    return ins_interface

def getGenSettings(connection: object, instrument_name: str) -> dict:

    table = 'general_settings'
    general_settings = {}
    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)
        
        get_instrument_query = cursor.mogrify("SELECT %s FROM %s WHERE cute_name = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_name))
        cursor.execute(get_instrument_query)
        result = cursor.fetchmany()
        general_settings = {key : value for key, value in zip(column_names, result[0])}

    return general_settings


def getModelOptions(connection: object, instrument_name: str) -> dict:

    table = 'model_and_options'
    model_options = {}

    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)

        get_instrument_query = cursor.mogrify("SELECT %s FROM %s WHERE cute_name = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_name))
        cursor.execute(get_instrument_query)
        result = cursor.fetchmany()

        for key, value in zip(column_names, result[0]):         
            model_options[key] =  value            

    return model_options


def getVisaSettings(connection: object, instrument_name: str) -> dict:

    table = 'visa'
    visa_settings = {}
    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)
        
        get_instrument_query = cursor.mogrify("SELECT %s FROM %s WHERE cute_name = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_name))
        cursor.execute(get_instrument_query)
        result = cursor.fetchmany()
        visa_settings = {key : value for key, value in zip(column_names, result[0])}
            
    return visa_settings


def getQuantities(connection: object, instrument_name: str) -> dict:

    table = 'quantities'
    quantities = {}
    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)

        get_quantity_names_query = "SELECT {column} FROM {table_name} WHERE cute_name = '{cute_name}';".format(column='label', table_name=table, cute_name=instrument_name)
        cursor.execute(get_quantity_names_query)
        quantity_names = cursor.fetchall()

        for quantity in quantity_names:
            get_quantity_query = cursor.mogrify("SELECT %s FROM %s WHERE cute_name = %s AND label = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_name, quantity[0]))
            cursor.execute(get_quantity_query)
            result = cursor.fetchmany()
            quantities[quantity[0]] = {key : value for key, value in zip(column_names, result[0])}

    return quantities


def getLatestValue(connection: object, instrument_name: str, label: str) -> str:
    table = 'quantities'
    latest_value = None
    with connection.cursor() as cursor:
        latest_value_query = "SELECT {column} FROM {table_name} WHERE cute_name = '{cute_name}' and label = '{label}';"\
            .format(column='latest_value', table_name=table, cute_name=instrument_name, label=label)
        cursor.execute(latest_value_query)
        latest_value = cursor.fetchone()[0]

    return latest_value


def setLatestValue(connection: object, latest_value: str, instrument_name: str, label: str):
    table = 'quantities'
    with connection.cursor() as cursor:
        query = f"UPDATE {table} SET latest_value = '{latest_value}' WHERE cute_name = '{instrument_name}' and label = '{label}'"
        cursor.execute(query)
        connection.commit()