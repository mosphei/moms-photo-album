from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table, Text
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

class PersonModel(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    past_names = Column(String(255))
    # Establishes the link to the Photo model via the association table
    photos: Mapped[list['PhotoModel']] = relationship("PhotoModel", secondary="photo_person_association", viewonly=True)

class PhotoModel(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey('users.id'))
    # We typically store the photo file path/URL, not the photo data itself, in the DB
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    # original filename
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_taken: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_uploaded: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # hashing for find duplicate photos
    hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    md5sum: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    # Establishes the link to the Person model via the association table
    people: Mapped[list[PersonModel]] = relationship("PersonModel", secondary="photo_person_association")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    admin = (Column(Boolean, default=False))
    Column('person_id', Integer, ForeignKey('people.id'), primary_key=True)

class UserSession(Base):
    __tablename__ = "sessions"
    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)