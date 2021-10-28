

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from psycopg2 import connect
from . import settings 

def con():
    return connect(f"""
    host={settings.DB_HOST}
    port={settings.DB_PORT}
    user={settings.DB_USER}
    password={settings.DB_PASSWORD}
    dbname={settings.DB_NAME}
    """)

engine = create_engine("postgresql://",creator=con)

Session = sessionmaker(bind=engine)
