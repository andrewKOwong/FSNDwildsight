#!/usr/bin/env python3
import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# SQLAlchemy database class to inherit from
Base = declarative_base()


# Wildsight users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Sighting types (e.g. Flower, Plant, etc.)
class SightingType(Base):
    __tablename__ = 'sighting_type'

    id = Column(Integer, primary_key=True)
    type = Column(String(250), nullable=False)
    # Location of image file
    image = Column(String(250), nullable=False)

    # For data access via JSON
    @property
    def serialize(self):
        """Return object data for easy conversion to JSON"""
        return {
            'id': self.id,
            'type': self.type,
            'image': self.image
        }


# Individual sightings
class Sighting(Base):
    __tablename__ = 'sighting'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(2000))
    location = Column(String(200), nullable=False)
    sighting_type_id = Column(Integer, ForeignKey('sighting_type.id'))
    sighting_type = relationship(SightingType)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # For data access via JSON
    @property
    def serialize(self):
        """Return object data for easy conversion to JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'sighting_type_id': self.sighting_type_id,
            # Str representing sighting type
            'sighting_type': self.sighting_type.type
        }


# SQLite dialect
engine = create_engine('sqlite:///wildsight.db')

# Create the db
Base.metadata.create_all(engine)
