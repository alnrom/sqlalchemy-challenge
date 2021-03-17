import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

measure = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def home():
    return (
        'Available routes: <br/>'
        'Precipitations: /api/v1.0/precipitation <br/>'
        'Stations:       /api/v1.0/stations <br/>'
        'Temperatures:   /api/v1.0/tobs <br/>'
        'Temperatures from date: /api/v1.0/startdate <br/>'
        'Temperatures between dates: /api/v1.0/startdate/enddate <br/>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    rain = session.query(measure.date, measure.prcp).filter(measure.date >= '2016-08-23').all()
    rain_dict = dict(rain)
    return jsonify(rain_dict)

@app.route("/api/v1.0/stations")
def stations():
    stat = session.query(station.station, station.name).all()
    stat_dict = dict(stat)
    return jsonify(stat_dict)

@app.route("/api/v1.0/tobs")
def temps():
    most_active = session.query(measure.station, measure.id).group_by(measure.station).order_by \
            (measure.id.desc()).all()
    top_station = most_active[0][0]
    temp_12m = session.query(measure.date, measure.station, measure.tobs).filter(measure.station == top_station)\
        .filter(measure.date >= '2016-08-23').all()
    keys = []
    values = []
    for tem in temp_12m:
        keys.append(tem[0])
        values.append(tem[2])
    pairs = zip(keys, values)
    dictio = dict(pairs)

    return jsonify(dictio)

@app.route("/api/v1.0/<start>")
def temps_start(start):
    temperatures = session.query(measure.date, measure.tobs).filter(measure.date > start).all()
    temps_list = []
    for temp in temperatures:
        temps_list.append(temp[1])
    tem = np.array(temps_list)
    mintemp = tem.min()
    maxtemp = tem.max()
    avgtemp = round(tem.mean(),2)
    keys = ['min', 'max', 'avg']
    values = [mintemp, maxtemp, avgtemp]
    dictio = dict(zip(keys, values))

    return jsonify(dictio)  

@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    temperatures = session.query(measure.date, measure.tobs).filter(measure.date > start)\
        .filter(measure.date < end).all()
    temps_list = []
    for temp in temperatures:
        temps_list.append(temp[1])
    tem = np.array(temps_list)
    mintemp = tem.min()
    maxtemp = tem.max()
    avgtemp = round(tem.mean(),2)
    keys = ['min', 'max', 'avg']
    values = [mintemp, maxtemp, avgtemp]
    dictio = dict(zip(keys, values))

    return jsonify(dictio)

if __name__ == "__main__":
    app.run(debug=True)

session.close()

