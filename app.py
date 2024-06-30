# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


#inspector = inspect(engine)
#print(inspector.get_table_names())

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


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
    return(
        f"Welcome to Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"   
        f"/api/v1.0/temp/<start>/<end><br/>"        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_12_months = dt.date(2016, 8, 23)
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_12_months).all()

    # create a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}
    
    session.close()
    
    return jsonify(precipitation_dict)

    
@app.route("/api/v1.0/stations")
def stations():    
    session = Session(engine)
    
    results = session.query(Station.station).all()
    
    session.close()
    
    station_list= [station[0] for  station in results]
    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():    
    session = Session(engine)
    
    last_12_months = dt.date(2017, 8, 23)  - dt.timedelta(days=365)
   # most_active = 'USC00519281'
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).\
                          first()[0]
                          
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= last_12_months).all()
    

    # dictionary
    temp_list = [{"date": date, "tobs": tobs} for date, tobs in results]
    
    return jsonify(temp_list)

    
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp(start, end=None):    
    session = Session(engine)
    
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    
    session.close()
    
    temp_dict = {
        "tmin": results[0][0],
        "tavg": results[0][1],
        "tmax": results[0][2]
    }

    return jsonify(temp_dict)


if __name__ == "__main__":
    app.run(debug=True)