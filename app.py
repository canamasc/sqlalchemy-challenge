from flask import Flask, jsonify

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
# home always has slash as above
def welcome():
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Find the most recent date in the data set.
    dates = session.query(Measurement.date)
    # can use max function because dates are formatted as YYYY-MM-DD
    most_recent_date= max(dates)[0]
    # Subtracts one year
    startdate1 = str(int(most_recent_date[0:4]) - 1) + most_recent_date[4:]
    startdate = dt.datetime(int(startdate1.split('-')[0]),
                       int(startdate1.split('-')[1]),
                       int(startdate1.split('-')[2]))

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, 
                        Measurement.prcp).filter(Measurement.date >= startdate).all()

    session.close()

   # Convert the query results to a dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    prec = {}
    for dates, rain in results:
        prec[dates] = rain 

    return jsonify(prec)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station, Station.name).all()

    session.close()
    all_stations = []
    for station, name in stations:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        all_stations.append(station_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Find the most recent date in the data set.
    dates = session.query(Measurement.date)
    # can use max function because dates are formatted as YYYY-MM-DD
    most_recent_date= max(dates)[0]
    # Subtracts one year
    startdate1 = str(int(most_recent_date[0:4]) - 1) + most_recent_date[4:]
    startdate = dt.datetime(int(startdate1.split('-')[0]),
                       int(startdate1.split('-')[1]),
                       int(startdate1.split('-')[2]))
    # Get most active station
    stations_count = engine.execute('SELECT station, COUNT(station) as station_count FROM measurement GROUP BY station ORDER BY station_count DESC').fetchall()
    most_act = stations_count[0][0]  

    #   Query the dates and temperature observations of the most active station for the last year of data.         
    resultstobs = session.query( Measurement.date, 
                Measurement.tobs).filter(Measurement.date >= startdate).filter(Measurement.station == most_act)
    
    session.close()
    all_tobs = []
    for dates,tobs in resultstobs:
        tobs_dict = {}
        tobs_dict['date'] = dates
        tobs_dict['tobs'] = tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)


if __name__ == "__main__":
    app.run(debug=True)
