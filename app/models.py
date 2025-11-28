from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column

Base = declarative_base()

# Association Table for the many-to-many relationship
# It only needs to store the foreign keys
photo_person_association = Table(
    'photo_person_association',
    Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id'), primary_key=True),
    Column('person_id', Integer, ForeignKey('people.id'), primary_key=True)
)

class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    # Establishes the link to the Photo model via the association table
    photos = relationship("Photo", secondary=photo_person_association, back_populates="people")

class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey('users.id'))
    # We typically store the photo file path/URL, not the photo data itself, in the DB
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_taken = Column(DateTime, nullable=True, index=True)
    date_uploaded = Column(DateTime, default=datetime.utcnow)
    # hashing for find duplicate photos
    hash = Column(String(64), nullable=True)
    # Establishes the link to the Person model via the association table
    people = relationship("Person", secondary=photo_person_association, back_populates="photos")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    Column('person_id', Integer, ForeignKey('people.id'), primary_key=True)
