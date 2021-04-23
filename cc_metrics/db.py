

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from psycopg2 import connect
from . import config

def con():
    return connect(f"""
    host={config.config('DB_HOST')}
    user={config.config('DB_USER')}
    password={config.config('DB_PASSWORD')}
    dbname={config.config('DB_NAME')}
    """)

engine = create_engine("postgresql://",creator=con)

Session = sessionmaker(bind=engine)
