from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType

# Hook up db engine to a Session class
engine = create_engine('sqlite:///wildsight.db')
Session = sessionmaker(bind=engine)
# Instantiate a session to access the db
session = Session()

# TODO convert csv file to database adding thing

# Soemthing like
# - read the csv
# - 
# - session.add_all([List of Sighting/Sighting Type objects])
# - session.commit()