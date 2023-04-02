-- contains instrument and connection details
CREATE TABLE IF NOT EXISTS instruments (
	cute_name TEXT PRIMARY KEY NOT NULL,
	manufacturer TEXT NOT NULL,
	interface TEXT NOT NULL, 
	address TEXT,
	serial BOOLEAN,
	visa BOOLEAN
);

-- Custom types for general_settings table
DO $$ BEGIN
    CREATE TYPE drivertype AS ENUM ('Auto', 'None', 'CR', 'LF', 'CR+LF');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- contains basic info of the instrument driver
CREATE TABLE IF NOT EXISTS general_settings (
	cute_name TEXT PRIMARY KEY REFERENCES instruments(cute_name),
	name TEXT NOT NULL, 
	ini_path TEXT NOT NULL,
	driver_path TEXT,
	interface TEXT DEFAULT 'GPIB',
	address TEXT,
	startup TEXT DEFAULT 'Set config',
	driver_type drivertype,
	upload_datetime TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_and_options (
	cute_name TEXT PRIMARY KEY REFERENCES instruments(cute_name),
	check_model BOOLEAN DEFAULT false,
	model_cmd TEXT DEFAULT '*IDN?',
	models TEXT[],
	model_ids TEXT[],
	check_options BOOLEAN,
	option_cmd TEXT,
	options TEXT[],
	option_ids TEXT[],
	-- option_cmd must be defined if check_options is true
	CONSTRAINT option_cmd_if_check_options
		CHECK ((NOT check_options) OR (option_cmd IS NOT NULL))
);

-- custom types used for visa table
DO $$ BEGIN
    CREATE TYPE termination AS ENUM ('Auto', 'None', 'CR', 'LF', 'CR+LF');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE paritytype AS ENUM ('No parity', 'Odd parity', 'Even parity');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- VISA settings of driver
CREATE TABLE IF NOT EXISTS visa (
	cute_name TEXT PRIMARY KEY REFERENCES instruments(cute_name),
	use_visa BOOLEAN,
	reset BOOLEAN DEFAULT false,
	query_instr_errors BOOLEAN,
	error_bit_mask INTEGER,
	error_cmd TEXT,
	init TEXT,
	final TEXT,
	str_true TEXT DEFAULT '1',
	str_false TEXT DEFAULT '0',
	str_value_out TEXT DEFAULT '%.9e%',
	str_value_strip_start INTEGER DEFAULT 0,
	str_value_strip_end INTEGER DEFAULT 0,
	always_read_after_write BOOLEAN DEFAULT false,
	timeout INTEGER, -- in seconds
	term_char termination,
	send_end_on_write BOOLEAN,
	supress_end_on_read BOOLEAN,
	baud_rate INTEGER DEFAULT 9600,
	data_bits INTEGER DEFAULT 8,
	stop_bits FLOAT DEFAULT 1,
	parity paritytype,
	gpib_board INTEGER DEFAULT 0,
	gpib_go_to_local BOOLEAN DEFAULT false,
	tcpip_specify_port BOOLEAN DEFAULT false,
	tcpip_port TEXT,
	CONSTRAINT tcpip_port_specified CHECK ((NOT tcpip_specify_port) OR (tcpip_port IS NOT NULL))
);

-- custom types used for quantities table
DO $$ BEGIN
    CREATE TYPE datatype AS ENUM ('DOUBLE', 'BOOLEAN', 'COMBO', 'STRING', 'COMPLEX',
	'VECTOR', 'VECTOR_COMPLEX', 'PATH', 'BUTTON');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE permissiontype AS ENUM ('BOTH', 'READ', 'WRITE', 'NONE');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


/* 	Stores data about the general_settings quantities
	This is most often under General Settings, Visa Settings, and Model sections
	Includes sections such as [Function], [Frequency], [Voltage], etc
	Section name is stored as label unless the driver specifies a label for that section
*/
CREATE TABLE IF NOT EXISTS quantities (
	cute_name TEXT REFERENCES instruments(cute_name),
	label TEXT,
	data_type datatype,
	unit TEXT,
	def_value TEXT,
	tool_tip TEXT,
	low_lim TEXT DEFAULT '-INF',
	high_lim TEXT DEFAULT '+INF',
	x_name TEXT,
	x_unit TEXT,
	combo_cmd JSON, /* Contains JSON in format of
					{
						combo_def_1: cmd_def_1,
						...
						combo_def_n: cmd_def_n
					}
					*/

	-- "group" is a reserved word. Renamed the below attribute to "groupname".
	groupname TEXT,
	section TEXT,
	state_quant TEXT,
	state_values TEXT[],
	model_values TEXT[],
	option_values TEXT[],
	permission permissiontype DEFAULT 'BOTH',
	show_in_measurement_dlg BOOLEAN,
	set_cmd TEXT,
	get_cmd TEXT DEFAULT 'set_cmd?',
	latest_value TEXT,
	PRIMARY KEY (cute_name, label)
);

-- ALTER TABLE quantities RENAME COLUMN "groupname" TO "group";

