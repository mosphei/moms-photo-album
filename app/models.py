from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association Table for the many-to-many relationship
# It only needs to store the foreign keys
image_person_association = Table(
    'image_person_association',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id'), primary_key=True),
    Column('person_id', Integer, ForeignKey('people.id'), primary_key=True)
)

class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    # Establishes the link to the Image model via the association table
    images = relationship("Image", secondary=image_person_association, back_populates="people")

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey('users.id'))
    # We typically store the image file path/URL, not the image data itself, in the DB
    file_path = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_taken = Column(DateTime, nullable=True, index=True)
    date_uploaded = Column(DateTime, default=datetime.utcnow)
    # hashing for find duplicate images
    hash = Column(String(64), nullable=True)
    # Establishes the link to the Person model via the association table
    people = relationship("Person", secondary=image_person_association, back_populates="images")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    Column('person_id', Integer, ForeignKey('people.id'), primary_key=True)
