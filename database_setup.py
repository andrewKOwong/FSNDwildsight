import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class SightingType(Base):
    __tablename__ = 'sighting_type'

    id = Column(Integer, primary_key = True)
    type = Column(String(250), nullable = False)

class Sighting(Base):
    __tablename__ = 'sighting'

    id = Column(Integer, primary_key = True)
    title = Column(String(250), nullable = False)
    description = Column(String(2000))
    coords = Column(String(200), nullable = False)
    sighting_type_id = Column(Integer, ForeignKey('sighting_type.id'))
    sighting_type = relationship(SightingType)

## TODO investigate serialization function.

# SQLite dialect
engine = create_engine('sqlite:///wildsight.db')

Base.metadata.create_all(engine)