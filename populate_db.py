#!/usr/bin/env python3
import pandas as pd

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType, Base, User

# Read in some demo data
# Pandas is convenient for handling csvs
DEMO_DATA_SIGHTINGS_FILE = 'demo_data/sightings_data.csv'
DEMO_DATA_TYPE_FILE = 'demo_data/sighting_type_data.csv'
DEMO_DATA_USERS_FILE = 'demo_data/user_data.csv'
demo_data = pd.read_csv(DEMO_DATA_SIGHTINGS_FILE)
demo_types = pd.read_csv(DEMO_DATA_TYPE_FILE)
demo_users = pd.read_csv(DEMO_DATA_USERS_FILE)

# Hook up db engine to a Session class
engine = create_engine('sqlite:///wildsight.db')
Session = sessionmaker(bind=engine)
Base.metadata.bind = engine
# Instantiate a session to access the db
session = Session()

# Create user database
for i in demo_users.index:
    data = demo_users.loc[i, :]
    new_user = User(name=data['user_name'],
                    email=data['email'])
    session.add(new_user)
    session.commit()


# Create sighting type objects
for i in demo_types.index:
    data = demo_types.loc[i, :]
    new_type = SightingType(type=data['type'],
                            image=data['image'])
    session.add(new_type)
    session.commit()


# Add and commit all sightings
# Use query to get the sighting type for each sighting
for i in demo_data.index:
    data = demo_data.loc[i, :]
    sighting_type = session.query(SightingType).filter_by(
                                type=data['sighting_type']).one()
    user = session.query(User).filter_by(id=int(data['user_id'])).one()
    new_sighting = Sighting(title=data['title'],
                            description=data['description'],
                            location=data['location'],
                            sighting_type=sighting_type,
                            user=user)
    session.add(new_sighting)
    session.commit()


session.close()
