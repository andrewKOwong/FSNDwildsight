#!/usr/bin/env python3
from builtins import type as typeof # For debugging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType, Base

from sighting_form import SightingForm

from flask import Flask, escape, render_template, request, redirect, url_for, flash
app = Flask(__name__)

# Use of Flask-SQLAlchemy is recommended to avoid # multi threading issues.
# See https://docs.sqlalchemy.org/en/13/orm/contextual.html 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wildsight.db'
db = SQLAlchemy(app)
session = db.session

# Old non Flask SQLAlchemy code
#from sqlalchemy.orm import sessionmaker
#engine = create_engine('sqlite:///wildsight.db')
#Base.metadata.bind = engine
#DBSession = sessionmaker(bind=engine)
#session = DBSession()

# Home page displays categories of sighting types
@app.route('/')
def home():
    #sighting_type = session.query(SightingType).first()
    #sightings = session.query(Sighting).filter_by(sighting_type_id = sighting_type.id)
    types = session.query(SightingType) # Sighting Types are pre-ordered before db creation
    sightings = session.query(Sighting)
    return render_template('index.html', sightings=sightings, types=types)

# Displays sightings of a particular type
@app.route('/types/<type>/')
def type_home(type):
    type_id = request.args.get('type_id')
    sightings = session.query(Sighting).filter_by(sighting_type_id=type_id)
    return render_template('type_home.html', sightings=sightings, type=type)

# Placeholder pages to create, edit, and delete pages
@app.route('/submit_sighting/', methods = ['GET', 'POST'])
def create_sighting():
    sighting_types = session.query(SightingType)
    form = SightingForm()
    form.sighting_type.choices = [(type.id, type.type) for type in sighting_types]
    print(form.validate_on_submit())
    for f, m in form.errors.items():
        for err in m:
            print(f)
            print(err)
    print(form.sighting_type.raw_data)
    if form.validate_on_submit():
        flash("New sighting created!")
        return redirect(url_for('home'))             
    
    return render_template('new_sighting.html', form=form)

@app.route('/sightings/<type>/<int:id>/edit/', methods=['GET', 'POST'])
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
        
        session.add(sighting)
        session.commit()

        flash("Sighting successfully edited!")
        return redirect(url_for('home'))

    else:
        sighting = session.query(Sighting).filter_by(id = id).one()
        current_sighting_type = sighting.sighting_type
        other_sighting_types = session.query(SightingType).filter(SightingType.id != current_sighting_type.id)
        return render_template('edit_sighting.html', 
                                sighting=sighting, 
                                current_sighting_type=current_sighting_type,
                                other_sighting_types=other_sighting_types)

@app.route('/sightings/<type>/<int:id>/delete/', methods=['GET','POST'])
def delete_sighting(type, id):
    sighting = session.query(Sighting).filter_by(id=id).one()
    if request.method == 'POST':
        session.delete(sighting)
        session.commit()
        flash("Sighting deleted!")
        return redirect(url_for('home'))
    else:
        return render_template('delete_sighting.html', sighting=sighting)

# Displays types available
@app.route('/types/')
def list_types():
    types = session.query(SightingType)
    output = ''
    for i in types:
        output += i.type
        output += '</br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'placeholder_secret_key'
    app.run(host = '0.0.0.0', port = 5000)