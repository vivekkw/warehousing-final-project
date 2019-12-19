#import relevant modules
import mysql.connector
import pandas as pd
from datetime import datetime
from datetime import timedelta

#credentials for loging into the database
db_username = "awesometeam"
db_password = "nandan123"
db_name = "test"
db_endpoint = "big-apple.cbx9jy53wa9n.us-east-2.rds.amazonaws.com"

#RDS configuration settings
config = {
  'user': db_username,
  'port': '3306',
  'password': db_password,
  #RDS instace endpoint
  'host': db_endpoint,
  'database': db_name,
  'raise_on_warnings': True
}

#general aesthetics settings
colors = ['#FFFFFF', '#D79922', '#F13C20', '#EFE2BA', '#4056A1', '#C5CBE3']

##############################################
####           Accidents Queries          ####
##############################################

def groupby_hour():
    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT HOUR(crash_time), "
                   "SUM(number_of_persons_injured), SUM(number_of_pedestrians_injured), "
                   "SUM(number_of_cyclist_injured), SUM(number_of_motorist_injured)"
                   "FROM accidents GROUP BY HOUR(crash_time)"
                  )

    by_hour = pd.DataFrame(cursor.fetchall())
    by_hour.columns = ['hour', 'persons_injured', 'pedestrians_injured' ,'cyclists_injured', 'motorists_injured']


    by_hour.index = pd.to_datetime(by_hour.hour, format = '%H')
    by_hour.index = by_hour.index.strftime('%H:%M')
    cursor.close()
    cnx.close()

    return by_hour
def groupby_borough():
    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT borough, "
                   "SUM(number_of_persons_injured), SUM(number_of_pedestrians_injured), "
                   "SUM(number_of_cyclist_injured), SUM(number_of_motorist_injured)"
                   "FROM accidents GROUP BY borough"
                  )

    by_borough = pd.DataFrame(cursor.fetchall())
    by_borough.columns = ['borough', 'persons_injured', 'pedestrians_injured' ,'cyclists_injured', 'motorists_injured']
    by_borough.borough[0] = 'NOT REPORTED'
    by_borough = by_borough.set_index('borough')
    by_borough = by_borough.apply(pd.to_numeric)

    cursor.close()
    cnx.close()

    return by_borough
def get_cause_injured():

    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT contributing_factor_vehicle_1, COUNT(contributing_factor_vehicle_1), SUM(number_of_pedestrians_injured), SUM(number_of_cyclist_injured), SUM(number_of_motorist_injured) FROM accidents GROUP BY contributing_factor_vehicle_1  ORDER BY COUNT(contributing_factor_vehicle_1) DESC LIMIT 6")
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ['cause', 'count', 'pedestrians', 'cyclists', 'motorists']
    df.set_index('cause', inplace =True)


    try:
        df.drop(labels=['Unspecified'], inplace = True)
    except:
        print("Unspecified was not part of the contirubting factors")

    cursor.close()
    cnx.close()

    return df
def get_sunburst_df(df):
    row, col = df.shape
    labels = ["Top 5 Causes of Accidents"]
    parents = [""]
    values = [df['count'].sum()]
    cols = [colors[0]]
    for r in range(row):
        labels.append(df.iloc[[r]].index[0])
        parents.append("Top 5 Causes of Accidents")
        values.append(df.iloc[r,0])
        cols.append(colors[r+1])
        for c in range(1,col):
            parents.append(df.iloc[[r]].index[0])
            labels.append(df.columns[c])
            values.append(df.iloc[r,c])
            cols.append(colors[r+1])

    return pd.DataFrame({'labels': labels, 'parents': parents, 'number': values, 'colors': cols})

##############################################
####           Calss 311 Queries          ####
##############################################

def locations_311():

    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT unique_key, agency_name, complaint_type, descriptor, latitude, longitude FROM 311_calls WHERE latitude IS NOT NULL AND longitude IS NOT NULL;")
    df_locations = pd.DataFrame(cursor.fetchall())

    #Close connection
    cnx.close()
    df_locations = df_locations.rename(columns={0: "unique_key", 1:
     "agency_name", 2: "complaint_type", 3:"descriptor",
     4:"latitude", 5:"longitude"})

    return(df_locations)
def locations_top10types_311():

    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT DISTINCT(complaint_type) AS complaint_types FROM 311_calls GROUP BY complaint_types ORDER BY count(unique_key) DESC LIMIT 10;")
    df_locations = pd.DataFrame(cursor.fetchall())

    #Close connection
    cnx.close()

    return(df_locations)

##############################################
####           Events Queries             ####
##############################################

def events_data():

    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT * FROM events")
    df_events = pd.DataFrame(cursor.fetchall())
    cursor.execute('SHOW COLUMNS FROM events')
    columns = cursor.fetchall()

    #Close connection
    cnx.close()

    column_names = [c[0] for c in columns]
    df_events.columns = column_names
    return(df_events)
def events_by_date():

    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT event_borough, DATE(start_date_time) AS start_date, \
    COUNT(event_id) AS event_count FROM events GROUP BY event_borough, start_date")
    df_events = pd.DataFrame(cursor.fetchall())

    #Close connection
    cnx.close()

    return(df_events)
def events_heatmap():

    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT date(start_date_time) AS dates, event_type, event_borough, COUNT(event_id) AS event_count \
    FROM events GROUP BY event_type, event_borough, dates ORDER BY dates")
    df_events = pd.DataFrame(cursor.fetchall())

    #Close connection
    cnx.close()

    df_events = df_events.rename(columns={0: "dates", 1: "event_type", 2: "event_borough", 3:"event_count"})
    df_events['dates_dt'] =  pd.to_datetime(df_events.dates)

    return(df_events)
def event_type_unique():

    #Setup the connector
    cnx = mysql.connector.connect(**config, use_pure=True)
    cursor = cnx.cursor()

    cursor.execute("SELECT event_type FROM events GROUP BY event_type ORDER BY event_type")
    df_event_type = pd.DataFrame(cursor.fetchall())

    #Close connection
    cnx.close()

    return(df_event_type)
