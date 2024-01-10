from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from dotenv import load_dotenv
load_dotenv()

import os


SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Base = automap_base()
Base.prepare(engine, reflect=True)

def get_db():
    try:
        db = Session(engine)
        yield db
    finally:
        db.close()