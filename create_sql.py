import sqlite3
import pandas as pd
import csv


#meteo.db is the sqlite db that will be created
sql = sqlite3.connect('EarthQuakes.db')
cur = sql.cursor()
csv_file = open('earthquakes_last_month.csv','r', errors='ignore')
next(csv_file, None)
reader = csv.reader(csv_file)



def create_sqlite_table():
    #Delete table if it already exists
    cur.execute('''DROP TABLE IF EXISTS earthquake_data''')
    #Create Table from csv file
    cur.execute('''CREATE TABLE IF NOT EXISTS earthquake_data
                (time DATETIME, 
                latitude REAL,
                longitude REAL, 
                depth REAL,
                mag REAL,
                magType TEXT,
                nst INTEGER,
                gap INTIGER,
                dmin REAL,
                rms REAL,
                net TEXT,
                id TEXT,
                updated DATETIME,
                place TEXT,
                type TEXT,
                horizontalError REAL,
                depthError REAL,
                magError REAL,
                magNst INTEGER,
                statue TEXT,
                location TEXT,
                magSource TEXT);''')
    #iterates through the table
    for row in reader:
        cur.execute('''INSERT INTO earthquake_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', row)

    #close the csv connection
    csv_file.close()


def create_df_from_db():
    #create a pandas dataframe from sql querry
    earthquake_df = pd.read_sql_query('SELECT time, latitude, longitude, depth FROM earthquake_data;', sql)


#Reuse this several times 
def close_sqlite_db():
    sql.commit()
    sql.close()


create_sqlite_table()
create_df_from_db()
close_sqlite_db()