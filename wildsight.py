#!/usr/bin/env python3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType, Base

from flask import Flask, escape, render_template, request, redirect, url_for
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

# Placeholder pages to create, edit, and delete pages
@app.route('/sightings/new/', methods = ['GET', 'POST'])
def create_sighting():
    if request.method == 'POST':
        sighting_type = session.query(SightingType).filter_by(type = request.form['sighting_type']).one()
        new_sighting = Sighting(title = request.form['title'],
                                description = request.form['description'],
                                location = request.form['location'],
                                sighting_type = sighting_type)
        session.add(new_sighting)
        session.commit()
        return redirect(url_for('create_sighting'))
        
    else:     
        sighting_types = session.query(SightingType)
        return render_template('new_sighting.html', sighting_types = sighting_types)

@app.route('/sightings/<type>/<int:id>/edit/', methods = ['GET', 'POST'])
def edit_sighting(type, id):
    if request.method == 'POST':
        sighting = session.query(Sighting).filter_by(id=id).one()
        sighting_type = session.query(SightingType).filter_by(type = request.form['sighting_type']).one()
        # Update required fields only if not empty
        if request.form['title']:
            sighting.title = request.form['title']
        if request.form['location']:
            sighting.location = request.form['location']
        if request.form['sighting_type']:
            sighting.sighting_type = sighting_type
        # Description is not required
        sighting.description = request.form['description']

        return redirect(url_for('home'))

    else:
        sighting = session.query(Sighting).filter_by(id = id).one()
        current_sighting_type = sighting.sighting_type
        other_sighting_types = session.query(SightingType).filter(SightingType.id != current_sighting_type.id)
        return render_template('edit_sighting.html', 
                                sighting=sighting, 
                                current_sighting_type=current_sighting_type,
                                other_sighting_types=other_sighting_types)

@app.route('/sightings/<type>/<int:id>/delete/')
def delete_sighting(type, id):
    return 'delete sighting'

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
    sighting_type = session.query(SightingType).filter_by(type=type).one()
    sightings = session.query(Sighting).filter_by(sighting_type=sighting_type)
    output = ''
    for i in sightings:
        output += i.title
        output += '</br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)