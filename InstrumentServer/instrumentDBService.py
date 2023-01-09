import psycopg2
from psycopg2.extensions import AsIs

def addGenSettings(connection, gen_settings: dict):
 
    id = None
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

        
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s RETURNING id;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))
        cursor.execute(insert_statement)
        id = cursor.fetchone()[0]

    return id

def addModelOptions(connection, model_options, id):

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

        columns.append('id')
        values.append(id)         
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))
        cursor.execute(insert_statement)


def addVisaSettings(connection, visa_settings: dict, id):

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

        columns.append('id')
        values.append(id)         
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))
        cursor.execute(insert_statement)

def addQuantity(connection, quantity: dict, id):

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

        columns.append('id')
        values.append(id)         
        insert_statement = cursor.mogrify("INSERT INTO %s (%s) VALUES %s;", (AsIs(table), AsIs(','.join(columns)), tuple(values)))        
        cursor.execute(insert_statement)

def getGenSettings(connection: object, instrument_id: str) -> dict:

    table = 'general_settings'
    general_settings = {}
    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)
        
        get_instrument_query = cursor.mogrify("SELECT %s FROM %s WHERE id = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_id))
        cursor.execute(get_instrument_query)
        result = cursor.fetchmany()
        general_settings = {key : value for key, value in zip(column_names, result[0])}

    return general_settings


def getModelOptions(connection: object, instrument_id: str) -> dict:

    table = 'model_and_options'
    model_options = {}

    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)

        get_instrument_query = cursor.mogrify("SELECT %s FROM %s WHERE id = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_id))
        cursor.execute(get_instrument_query)
        result = cursor.fetchmany()

        for key, value in zip(column_names, result[0]):         
            model_options[key] =  value            

    return model_options


def getVisaSettings(connection: object, instrument_id: str) -> dict:

    table = 'visa'
    visa_settings = {}
    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)
        
        get_instrument_query = cursor.mogrify("SELECT %s FROM %s WHERE id = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_id))
        cursor.execute(get_instrument_query)
        result = cursor.fetchmany()
        visa_settings = {key : value for key, value in zip(column_names, result[0])}
            
    return visa_settings


def getQuantities(connection: object, instrument_id: str) -> dict:

    table = 'quantities'
    quantities = {}
    with connection.cursor() as cursor:
        column_names_query = "SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';".format(table_name=table)            
        cursor.execute(column_names_query)
        column_names = cursor.fetchall()
        column_names = tuple(column_name[0] for column_name in column_names)

        get_quantity_names_query = "SELECT {column} FROM {table_name} WHERE id = '{id}';".format(column='label', table_name=table, id=instrument_id)
        cursor.execute(get_quantity_names_query)
        quantity_names = cursor.fetchall()

        for quantity in quantity_names:
            get_quantity_query = cursor.mogrify("SELECT %s FROM %s WHERE id = %s AND label = %s;", (AsIs(','.join(column_names)), AsIs(table), instrument_id, quantity[0]))
            cursor.execute(get_quantity_query)
            result = cursor.fetchmany()
            quantities[quantity[0]] = {key : value for key, value in zip(column_names, result[0])}

    return quantities
