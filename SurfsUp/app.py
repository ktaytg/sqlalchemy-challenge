"""
# Import the dependencies.
"""
import datetime as dt
import numpy as np
import pandas as pd

# * Import SQLalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# * Import Flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(autoload_with = engine)


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

#Define the Welcome Route
@app.route("/")
def welcome():
    # * Listing avaiable API roots
    return (
        f"Welcome to Surf's Up!: Honolulu, Hawaii Climate API! <br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/2016-08-22<br/>"
        f"/api/v1.0/temp/2013-08-22/2016-08-22"
    )


##################################################################


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    #Open session
    session = Session(engine)

    # Convert the query results from your precipitation analysis\
    # (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    # Return precipitation data
    prv_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date > "2016-08-22")
        .order_by(Measurement.date)
        .all()
    )
    session.close()
    # adding  the list of tuples into normal list
    prcp_results = []
    for data in prv_data:
        prcp_results.append(data)
    # forming  a dictionary with the list of tuples
    prcp = dict(prcp_results)
    return jsonify(prcp)


##########################################################################
#Define the Stations Route
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    #Open session
    session = Session(engine)
    #Return a JSON list of stations from the dataset
    all_stations = session.query(Station.name).all()
    session.close()
    # Convert list of tuples into normal list
    stations_data = list(np.ravel(all_stations))
    return jsonify(stations_data)


###############################################################################
#Define the TOBS Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    #Open session
    session = Session(engine)
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    tobs_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == "USC00519281")
        .filter(Measurement.date > "2016-08-22")
    )
    tobs_results = []
    for i in tobs_data:
        tobs_results.append(i)
    session.close()
    #converting our result to dictionary format date as key and temp as value
    temperature_data = dict(tobs_results)
    return jsonify(temperature_data)


#######################################################################
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/temp/<start>")
def stats(start):
# Create our session (link) from Python to the DB
#Open session
    session = Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    cal = [
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]
    results = session.query(*cal).filter(Measurement.date >= start).all()
    session.close()
    #storing results in dictionary format
    temps_list = []
    for data in results:
        temps_dict = {}
        (min_temp, avg_temp, max_temp) = data
        temps_dict["min_temp"] = min_temp
        temps_dict["max_temp"] = max_temp
        temps_dict["avg_temp"] = avg_temp
        temps_list.append(temps_dict)
    return jsonify(temps_list)


#############################################################################

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/temp/<start>/<end>")
def stat(start, end):
# Create our session (link) from Python to the DB
    session = Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(end, "%Y-%m-%d").date()
    cal = [
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]
    results = (
        session.query(*cal)
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )
    session.close()
    temp_list = []
    #storing results in dictionary format
    for result in results:
        temp_dict = {}
        (temp_min, temp_avg, temp_max) = result
        temp_dict["min_temp"] = temp_min
        temp_dict["max_temp"] = temp_max
        temp_dict["avg_temp"] = temp_avg
        temp_list.append(temp_dict)
    return jsonify(temp_list)


if __name__ == "__main__":
    app.run(debug=True)