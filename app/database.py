import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.declarative import declarative_base
from models import Base

# Database connection details using environment variables
DB_HOST = os.getenv("DB_HOST",'db') # The service name defined in docker-compose.yml
DB_NAME = os.getenv("DB_NAME",'fastapi_db')
DB_USER = os.getenv("DB_USER",'xxx') 
DB_PASS = os.getenv("DB_PASS",'xxx') 
DB_PORT = 3306        # Default MySQL port

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True # Optional, helps manage connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all_tables():
    # This will create tables defined using Base in your models.py file
    Base.metadata.create_all(bind=engine)

#from fastapi.encoders import jsonable_encoder

def update_data_in_db(db_model, update_schema):
    update_data = update_schema.model_dump(exclude_unset=True) # Use .dict(exclude_unset=True) in Pydantic v1
    for key, value in update_data.items():
        setattr(db_model, key, value)

    return db_model
