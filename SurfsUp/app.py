# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create the SQLAlchemy engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base() 
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f" /api/v1.0/temp/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results from your precipitation analysis
    last_day = dt.date(2017, 8, 23)
    year = last_day - dt.timedelta(days=365)
    query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year).all()
    precipitation_dict = {}
    for result in query:
        date = result[0]
        precipitation = result[1]
        precipitation_dict[date] = precipitation
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def station():
    # Create a new session
    session = Session(engine)
    # Query
    results = session.query(stations.station).all()
    # station names
    station_list = [station for station, in results]
    # Close the session
    session.close()
    #get json
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Open a new session
    session = Session(engine)
    
    # Establish last day
    last_day = dt.date(2017, 8, 23)
    
    # Establish year from last day
    year = last_day - dt.timedelta(days=365)
    
    # Query
    results = session.query(measurement.date, measurement.tobs).\
              filter(measurement.station == 'USC00519281').\
              filter(measurement.date >= year).all()
    
    # Create list
    tobs_list = [{'date': date, 'tobs': tobs} for date, tobs in results]
    
    # Close session
    session.close()
    
    # Get JSON 
    return jsonify(tobs_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<end>")
def stats(start=None, end=None):
    #open a session
    session = session(engine)
    
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]           
    
    # Query to calculate TMIN, TAVG, and TMAX based on the specified date range
    if not end:
        # Calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
        results = session.query(*sel).\
                    filter(measurement.date >= start).all()
    else:
        # Calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date (inclusive)
        results = session.query(*sel).\
                    filter(measurement.date >= start).\
                    filter(measurement.date <= end).all()
    
    # Create a dictionary to hold the result
    temp_stats = {}
    temp_stats['TMIN'] = results[0][0]
    temp_stats['TAVG'] = results[0][1]
    temp_stats['TMAX'] = results[0][2]

    #close session
    session.close()
    
    # Return the JSON representation of the result
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
