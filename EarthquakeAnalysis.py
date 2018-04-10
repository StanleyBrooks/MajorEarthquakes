from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import (GMapPlot, GMapOptions, ColumnDataSource, Circle, Range1d, PanTool, WheelZoomTool, BoxSelectTool)

import numpy as np
import pandas as pd
import json
import requests
import sqlite3
import csv


#creates sqlite db named EarthQuakes.db
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


def world_map():

    #Create pandas DataFrame from sqlite3 db
    earthquake_df = pd.read_sql_query('SELECT latitude, longitude, depth FROM earthquake_data;', sql)

    #remove NA values
    earthquake_df = earthquake_df.dropna()

    #Use pandas to convert strings into numbers(floats)
    earthquake_df['longitude'] = earthquake_df['longitude'].astype(float)
    earthquake_df['latitude'] = earthquake_df['latitude'].astype(float)
    output_file("world-map.html", title="Major Earthquakes, USA")

    #This section uses Bokeh patches and json data of country boundries to map the world.  This code
    #is a modified version of a project worked on by Ken Alger in the treehouse.com tutorial 
    #'Data Visualization with Bokeh' in the video 'Plotting the World'.  The map of the world
    #comes from Johan Sundström who has a github at https://github.com/johan/world.geo.json


    def world_map_json():

        url = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'
        r = requests.get(url)
        json_data = r.json()


        def get_coordinates(features):

            #This uses lambda(a small anonymous throwaway function) for list comprehensions to
            #check the depth is a list AND 

            #depth is a list and = equal to 
            depth = lambda L: isinstance(L, list) and max(map(depth, L))+1

            #Defines longitudes and latitudes as lists
            longitudes = []
            latitudes = []

            #this iterates through the json_data['freatures'] for each feature
            #each feature is json data for a country boundry, this makes lists of longitude and latitude
            #for each country boundry.  This is standard geo_json layout
            for feature in json_data['features']:
                coordinates = feature['geometry']['coordinates']
                number_dimensions = depth(coordinates)
                # one border
                if number_dimensions == 3:
                    
                    points = np.array(coordinates[0], 'f')
                    longitudes.append(points[:, 0])
                    latitudes.append(points[:, 1])
                    # several borders
                else:
                    for shape in coordinates:
                        points = np.array(shape[0], 'f')
                        longitudes.append(points[:, 0])
                        latitudes.append(points[:, 1])
            return longitudes, latitudes

        lats, longs = get_coordinates(json_data['features'])

        #took off hover for now due to performance issues
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

        #make a graph that is bound by Geographic Coordinates
        world_map_plot = figure(plot_width=900,
                                plot_height=600,
                                title="Major Earthquakes Worldwide in the past 30 days using JSON data for country shapes",
                                tools=TOOLS,
                                x_range=(-180, 180),
                                y_range=(-90, 90),
                                x_axis_label = "Longitude",
                                y_axis_label = "Latitude")

        world_map_plot.background_fill_color = "#f7fcb9"
        world_map_plot.background_fill_alpha = 0.55

        #This applies the geometic shapes to a lat,long grid
        world_map_plot.patches(lats, longs, line_color="black", fill_color="#99d8c9", fill_alpha=0.75, line_width=None)

        #Meteorite landings data mapped over the top of the world patch in red
        world_map_plot.scatter(earthquake_df['longitude'], earthquake_df['latitude'], fill_color="#e31a1c", fill_alpha=1, line_width=.5)

        #Show the data
        show(world_map_plot)

    world_map_json()


def close_sqlite_db():
    sql.commit()
    sql.close()


create_sqlite_table()
world_map()
close_sqlite_db()
