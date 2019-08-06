#!/usr/bin/env python3
import pandas as pd

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType

# Read in some demo data
DEMO_DATA_FILE = 'sightings_data.csv'
demo_data = pd.read_csv(DEMO_DATA_FILE)

# Hook up db engine to a Session class
engine = create_engine('sqlite:///wildsight.db')
Session = sessionmaker(bind=engine)
# Instantiate a session to access the db
session = Session()

# Create sighting type objects based on sighting_type column
# and place into a dict.
sighting_type_dict = {sighting_type:SightingType(type = sighting_type)
                     for sighting_type in demo_data.sighting_type.unique()}

# Add and commit all sighting types
for i in sighting_type_dict:
    session.add(sighting_type_dict[i])
    session.commit()

# Add and commit all sightings
for i in demo_data.index:
    new_sighting = Sighting(title = demo_data.loc[i,:]['title'], 
                            description= demo_data.loc[i,:]['description'],
                            location = demo_data.loc[i,:]['location'],
                            sighting_type = sighting_type_dict[demo_data.loc[i,:]['sighting_type']])
    session.add(new_sighting)
    session.commit()


session.close()


