# app/db/base.py

from sqlalchemy.orm import declarative_base
from .session import engine

Base = declarative_base()


def init():
    """
    Initialize the database by creating all tables.

    This function imports all the models to force the creation of the tables.
    """
    from app.db import models  
    print("DATABASE INITTT")
    Base.metadata.create_all(bind=engine)

