from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import (
    relationship,
    declarative_base,
    Mapped,
    mapped_column,
    column_property,
)
from sqlalchemy.dialects.mysql import LONGTEXT

Base = declarative_base()

# Association Table for the many-to-many relationship
# It only needs to store the foreign keys
photo_person_association = Table(
    "photo_person_association",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id"), primary_key=True),
    Column("person_id", Integer, ForeignKey("people.id"), primary_key=True),
)


class PersonModel(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    past_names: Mapped[str] = mapped_column(String(255))
    date_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    # Establishes the link to the Photo model via the association table
    photos: Mapped[list["PhotoModel"]] = relationship(
        "PhotoModel", secondary="photo_person_association", viewonly=True
    )


class PersonCountModel(Base):
    """
    CREATE VIEW person_photo_counts AS
    SELECT person_id as id,count(*) as photo_count, people.name, past_names
    FROM photo_person_association
    LEFT JOIN people ON person_id=people.id
    GROUP BY person_id
    """

    __tablename__ = "person_photo_counts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    past_names: Mapped[str] = mapped_column(String(255))
    photo_count: Mapped[int] = mapped_column(Integer)


class PhotoModel(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # We typically store the photo file path/URL, not the photo data itself, in the DB
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    # original filename
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)
    date_taken: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_uploaded: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    date_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    # image or video
    content_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    # hashing for find duplicate photos
    size: Mapped[int] = mapped_column(Integer)
    hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    md5sum: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    # Establishes the link to the Person model via the association table
    people: Mapped[list[PersonModel]] = relationship(
        "PersonModel", secondary="photo_person_association"
    )


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    admin = Column(Boolean, default=False)
    Column("person_id", Integer, ForeignKey("people.id"), primary_key=True)


class UserSession(Base):
    __tablename__ = "sessions"
    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


class SearchPersonModel(Base):
    __tablename__ = "searchpeople"
    q = mapped_column(String(255), nullable=False, primary_key=True)
    person_id = mapped_column(Integer, nullable=False, primary_key=True)
    relevance = mapped_column(Float, nullable=False)
    date_seen = mapped_column(DateTime, default=datetime.utcnow)


class SearchPhotoModel(Base):
    __tablename__ = "searchphotos"
    q = mapped_column(String(255), nullable=False, primary_key=True)
    photo_id = mapped_column(Integer, nullable=False, primary_key=True)
    relevance = mapped_column(Float, nullable=False)
    date_seen = mapped_column(DateTime, default=datetime.utcnow)
