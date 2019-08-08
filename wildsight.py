#!/usr/bin/env python3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType, Base

from flask import Flask, escape, render_template
app = Flask(__name__)

engine = create_engine('sqlite:///wildsight.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Displays all sightings
@app.route('/')
def home():
    #sighting_type = session.query(SightingType).first()
    #sightings = session.query(Sighting).filter_by(sighting_type_id = sighting_type.id)
    sightings = session.query(Sighting)
    return render_template('index.html', sightings=sightings)

# Displays types available
@app.route('/types/')
def list_types():
    types = session.query(SightingType)
    output = ''
    for i in types:
        output += i.type
        output += '</br>'
    return output

# Displays sightings of a particular type
@app.route('/types/<type>/')
def list_sightings_in_type(type):
    sighting_type = session.query(SightingType).filter_by(type = type).one()
    sightings = session.query(Sighting).filter_by(sighting_type = sighting_type)
    output = ''
    for i in sightings:
        output += i.title
        output += '</br>'
    return output

# Placeholder pages to create, edit, and delete pages
@app.route('/types/<type>/new/')
def create_sighting(type):
    return 'new sighting'

@app.route('/types/<type>/edit/')
def edit_sighting(type):
    return 'edit sighting'

@app.route('/types/<type>/delete/')
def delete_sighting(type):
    return 'delete sighting'

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)