# Import required packages
import requests
import mysql.connector
import os
from datetime import datetime
from datetime import timedelta

############################# Helper Functions ###############################
def get_data (url, start, end, key_col, key_list, date_col):

    """Function to connect to the database, extract the relevant data
    and reformat the data.
    """

    #Put start and end times into appropriate format for query
    start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%S")

    #Create query
    query_dates = "$where=" + date_col + " between " + "'" + start_str + "'" + " and " + "'" + end_str + "'" + "&$limit=50000"
    query = url + "$$app_token=" + os.environ['app_token'] + "&" + query_dates

    #Get data from API
    response = requests.get(query)
    data = response.json()

    #Extract relevant data from the JSON and store it as a dictionary
    data_formatted = []

    for row in data:
        dict_data = {key_col: row[key_col]}
        for key in key_list:
           if sum([i==key for i in row.keys()])==1:
               dict_data[key] = row[key]
           else:
                dict_data[key] = None
        data_formatted.append(dict_data)

    return data_formatted

def database_update (drop_query, create_query, insert_query, data):

    """Function to deletes the existing table, creates it again,
    and populates it with the data provided as an input.
    """

    #Setup the connector
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    #Drop the table
    try:
        cursor.execute(drop_query)
    except:
        print('Table does not exist')

    #Create table again
    cursor.execute(create_query)

    #Insert the data into the database
    for row in data:
       cursor.execute(insert_query, row)

    #Commit changes and close cursor
    cnx.commit()
    cursor.close()
    cnx.close()


############################# Environmental Variables ###############################

db_username = "awesometeam"
db_name = "test"
db_endpoint = "big-apple.cbx9jy53wa9n.us-east-2.rds.amazonaws.com"
#Specify app_token and db_password in 'Environmental Variables' section of Lambda Function

#RDS configuration settings
config = {'user': db_username,
            'port': '3306',
            'password': os.environ['db_password'],
            'host': db_endpoint,
            'database': db_name,
            'raise_on_warnings': True}

#datetime objects containing start and end dates for queries
now = datetime.now()
last_week = now - timedelta(weeks = 1)
next_4weeks = now + timedelta(weeks = 4)

#------------ 311 Calls -------------#

#HTTPS address for the API
url_311 = "https://data.cityofnewyork.us/resource/erm2-nwe9.json?"

keys_311 = ['unique_key',
            'created_date',
            'closed_date',
            'agency',
            'agency_name',
            'complaint_type',
            'descriptor',
            'incident_zip',
            'borough',
           'facility_type',
           'location_type',
            'status',
           'due_date',
            'resolution_action_updated_date',
            'x_coordinate_state_plane',
            'y_coordinate_state_plane',
            'open_data_channel_type',
            'latitude',
            'longitude']

#------------ Events -------------#

# HTTPS address for the API
url_events = "https://data.cityofnewyork.us/resource/tvpp-9vvx.json?"

keys_events = ['event_id', 'event_name', 'start_date_time', 'end_date_time',
               'event_agency', 'event_type', 'event_borough', 'event_location']


#------------ Accidents -------------#

# HTTPS address for the API
url_acc = "https://data.cityofnewyork.us/resource/h9gi-nx95.json?"

keys_acc =  ["collision_id", "crash_date", "crash_time",
             "borough", "zip_code", "latitude", "longitude",
             "number_of_persons_injured", "number_of_persons_killed",
             "number_of_pedestrians_injured", "number_of_pedestrians_killed",
             "number_of_cyclist_injured", "number_of_cyclist_killed",
             "number_of_motorist_injured", "number_of_motorist_killed",
             "contributing_factor_vehicle_1", "contributing_factor_vehicle_2"]

############################# MariaDB Queries ###############################

#------------ 311 Calls -------------#
drop_311_calls = ("DROP TABLE `311_calls`")

create_311_calls = (
   "CREATE TABLE `311_calls` ("
   "  `unique_key` INTEGER PRIMARY KEY,"
   "  `created_date` VARCHAR(30),"
   "  `closed_date` VARCHAR(30),"
   "  `agency` VARCHAR(30),"
   "  `agency_name` VARCHAR(1000),"
   "  `complaint_type` VARCHAR(1000),"
   "  `descriptor` VARCHAR(1000),"
   " `incident_zip` INTEGER,"
   "  `borough` VARCHAR(30),"
   "  `facility_type` VARCHAR(1000),"
   "  `location_type` VARCHAR(1000),"
   "  `status` VARCHAR(1000),"
   "  `due_date` VARCHAR(30),"
   "  `resolution_action_updated_date` VARCHAR(30),"
   "  `x_coordinate_state_plane` INTEGER,"
   "  `y_coordinate_state_plane` INTEGER,"
   "  `open_data_channel_type` VARCHAR(30),"
   "  `latitude` VARCHAR(30),"
   " `longitude` VARCHAR(30)"
   ") ENGINE=InnoDB")

calls_sql = (
   "insert into 311_calls"
   "(unique_key, created_date, closed_date, agency, agency_name, complaint_type,"
            "descriptor, location_type, incident_zip, borough, facility_type,"
            "status, due_date, resolution_action_updated_date, x_coordinate_state_plane,"
            "y_coordinate_state_plane, open_data_channel_type, latitude, longitude)"
   "values (%(unique_key)s, %(created_date)s, %(closed_date)s, %(agency)s, %(agency_name)s, %(complaint_type)s,"
            "%(descriptor)s, %(location_type)s, %(incident_zip)s, %(borough)s, %(facility_type)s,"
            "%(status)s, %(due_date)s, %(resolution_action_updated_date)s, %(x_coordinate_state_plane)s,"
            "%(y_coordinate_state_plane)s, %(open_data_channel_type)s, %(latitude)s, %(longitude)s)")

#------------ Events -------------#

drop_events = ("DROP TABLE `events`")

create_events = (
   "CREATE TABLE `events` ("
   "  `event_id` int(10) NOT NULL,"
   "  `event_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,"
   "  `start_date_time` datetime NOT NULL,"
   "  `end_date_time` datetime NOT NULL,"
   "  `event_agency` varchar(255),"
   "  `event_type` varchar(255),"
   "  `event_borough` varchar(255),"
   " `event_location` varchar (500),"
   "  PRIMARY KEY (`event_id`,`start_date_time`)"
   ") ENGINE=InnoDB")

events_sql = (
   "insert into events"
   "(event_id, event_name, start_date_time, end_date_time,"
    "event_agency, event_type, event_borough, event_location)"

    "values (%(event_id)s, %(event_name)s, %(start_date_time)s, %(end_date_time)s, %(event_agency)s, %(event_type)s,"
    "%(event_borough)s, %(event_location)s)")

#------------ Accidents -------------#

drop_accidents = ("DROP TABLE `accidents`")

create_accidents = (
    "CREATE TABLE `accidents` ("
    "  `collision_id` INTEGER PRIMARY KEY,"
    "  `crash_date` DATETIME,"
    "  `crash_time` TIME,"
    "  `borough` VARCHAR(30),"
    "  `zip_code` INTEGER,"
    "  `latitude` INTEGER,"
    "  `longitude` INTEGER,"
    "  `number_of_persons_injured` INTEGER,"
    "  `number_of_persons_killed` INTEGER,"
    "  `number_of_pedestrians_injured` INTEGER,"
    "  `number_of_pedestrians_killed` INTEGER,"
    "  `number_of_cyclist_injured` INTEGER,"
    "  `number_of_cyclist_killed` INTEGER,"
    "  `number_of_motorist_injured` INTEGER,"
    "  `number_of_motorist_killed` INTEGER,"
    "  `contributing_factor_vehicle_1` VARCHAR(1000),"
    "  `contributing_factor_vehicle_2` VARCHAR(1000)"
    ") ENGINE=InnoDB")

acc_sql = (
   "insert into accidents"
   "(collision_id, crash_date, crash_time, borough, zip_code, latitude, longitude,"
    "number_of_persons_injured, number_of_persons_killed, "
    "number_of_pedestrians_injured, number_of_pedestrians_killed, "
    "number_of_cyclist_injured, number_of_cyclist_killed, "
    "number_of_motorist_injured, number_of_motorist_killed, "
    "contributing_factor_vehicle_1, contributing_factor_vehicle_2)"

    "values (%(collision_id)s, %(crash_date)s, %(crash_time)s, %(borough)s, %(zip_code)s, %(latitude)s,"
    "%(longitude)s, %(number_of_persons_injured)s, %(number_of_persons_killed)s,"
    "%(number_of_pedestrians_injured)s, %(number_of_pedestrians_killed)s, %(number_of_cyclist_injured)s,"
    "%(number_of_cyclist_killed)s, %(number_of_motorist_injured)s, %(number_of_motorist_killed)s,"
    "%(contributing_factor_vehicle_1)s, %(contributing_factor_vehicle_2)s)")

###################### FUNCTION EXECUTION ##############################

def lambda_handler(event, context):

    # TODO implement

    #311 Calls
    data_311 = get_data(url_311, last_week, now, 'unique_key', keys_311, 'created_date')
    database_update (drop_311_calls, create_311_calls, calls_sql, data_311)
    print('Done. Calls 311 data introduced in the database')

    #Events
    events = get_data(url_events, now, next_4weeks, 'event_id', keys_events, 'start_date_time')
    database_update (drop_events, create_events, events_sql, events)
    print('Done. Events data introduced in the database')

    #Accidents
    accidents = get_data(url_acc, last_week, now, 'collision_id', keys_acc, 'crash_date')
    database_update (drop_accidents, create_accidents, acc_sql, accidents)
    print('Done. Accidents data introduced in the database')

    return {
        'statusCode': 200,
        'body': 'Load complete! With timer!'
    }
