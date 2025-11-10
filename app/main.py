from fastapi import FastAPI
import pymysql.cursors
import time
import os

app = FastAPI()

# Database connection details using environment variables
DB_HOST = "db" # The service name defined in docker-compose.yml
DB_NAME = "fastapi_db"
DB_USER = os.getenv("DB_USER",'xxx') 
DB_PASS = os.getenv("DB_PASS",'xxx') 

def get_db_connection():
    # Wait for the database to be ready (optional but recommended)
    #for _ in range(3):
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor)
        return connection
    except Exception as ex:
        #print(f"Database not ready, retrying in 5 seconds...")
        #time.sleep(1)
        raise Exception(f"Could not connect to the database {DB_HOST}.{DB_NAME} as {DB_USER}:{DB_PASS}...{ex}")

@app.get("/")
def read_root():
    return {"Hello": "World."}

@app.get("/db-status")
def db_status():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "connected", "server_time": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# You can add more endpoints for CRUD operations using SQLAlchemy or raw SQL
