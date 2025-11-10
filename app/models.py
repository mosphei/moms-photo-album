from sqlalchemy import Column, Integer, String, ForeignKey, Table
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
    name = Column(String, index=True)
    # Establishes the link to the Image model via the association table
    images = relationship("Image", secondary=image_person_association, back_populates="people")

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    # We typically store the image file path/URL, not the image data itself, in the DB
    file_path = Column(String, nullable=False)
    description = Column(String, nullable=True)
    # Establishes the link to the Person model via the association table
    people = relationship("Person", secondary=image_person_association, back_populates="images")
