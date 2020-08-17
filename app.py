import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

##########Database setup###################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect and existing database into a new model
Base=automap_base()
#reflect the tables
Base.prepare(engine, reflect = True)

#Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

###########Flask Setup#################
app = Flask(__name__)

############Flask Routes###############
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available api routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_data_point=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year=dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_query = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >=last_year).all()

    session.close()

#Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_list = []
    for date, prcp in precipitation_query:
        if prcp != None:
            precipitation_dict = {}
            precipitation_dict[date] = prcp
            precipitation_list.append(precipitation_dict)

    #Return the JSON representation of your dictionary.
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query List of the stations
    stations_data = session.query(Station.station, Station.name, 
                    Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    """List of stations from the Data Set"""
    #Return a JSON list of stations from the dataset.
    all_stations = list(np.ravel(stations_data))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_data_point=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year=dt.date(2017,8,23) - dt.timedelta(days=365)    
    
    # Choose the station with the highest number of temperature observations.
    high_temp_observ =session.query(Measurement.station,func.count(Measurement.tobs)).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).all()
    
    #Query the dates and temperature observations of the most active station for the last year of data.
    temperature=session.query(Measurement.station,Measurement.date,Measurement.tobs).\
        filter(Measurement.station=="USC00519281").\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    session.close()
    """List of temperature observations (TOBS) of the most active station for the previous year"""
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    all_observations = list(np.ravel(temperature))

    return jsonify(all_observations)

@app.route("/api/v1.0/<start>/")
def date(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)

    
    start=dt.date(2017,8,23) - dt.timedelta(days=365)
    
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    temperature_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()
    """List of the minimum temperature, the average temperature, and the max temperature for a given start range."""
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range.
    temp_observations = list(np.ravel(temperature_results))

    return jsonify(temp_observations)

@app.route("/api/v1.0/<start>/<end>/")
def dates(start,end):

    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    end=dt.date(2017,8,23)
    start=dt.date(2017,8,8) 

    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    dates_results=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
      

    session.close() 

    """List of the minimum temperature, the average temperature, and the max temperature for a given start-end range."""
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range.
    dates_observations = list(np.ravel(dates_results))

    return jsonify(dates_observations)  

if __name__ == '__main__':
    app.run(debug=True)





