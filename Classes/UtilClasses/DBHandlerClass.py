from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

import os
from datetime import datetime, timedelta

# Instantiate declarative base. Necessary for declaring tables as classes
Base = declarative_base()


@contextmanager
def session_scope(dbms):
    """Provide a transactional scope around a series of operations."""
    session = dbms.Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class DBHandler:
    SQLITE = 'sqlite'

    # Table Names
    VACANCIES = 'vacancies'
    PLATFORM = 'platform'

    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    DB_ENGINE = {
        SQLITE: f"sqlite:///{os.getcwd()}\\"
    }

    # Main DB Connection Ref Obj
    db_engine = None

    def __init__(self, dbtype, db_name):
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype] + db_name
            self.db_engine = create_engine(engine_url)
            print(self.db_engine)
        else:
            raise ValueError("DBType does not exist!")

        self.Session = sessionmaker(bind=self.db_engine)

        self.initial_platform_data = [
            Platform(name="karriere.at", base_address="www.karriere.at/"),
        ]

    def get_session(self):
        return self.Session()

    def create_database_and_tables(self):
        try:
            Base.metadata.create_all(self.db_engine)
            print("Tables created")

        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def cleanup_job_postings_in_database(self):
        """Delete all job postings that are older than the configured day-limit"""
        if ConfigHandler.POSTING_RETENTION_IN_DAYS is None:
            # If is set to None, auto-deletion is disabled
            return None

        else:
            posting_age_limit = datetime.now() - timedelta(days=ConfigHandler.POSTING_RETENTION_IN_DAYS)

            with session_scope(self) as session:
                session.query(Vacancies).filter(Vacancies.date < posting_age_limit).delete()

    def get_tables_in_database(self):
        table_query = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        result = self.execute_query(table_query, select_query=True)
        return result

    def load_initial_data(self):
        with session_scope(self) as session:
            for platform_instance in self.initial_platform_data:
                session.add(platform_instance)

    def execute_query(self, query, select_query: bool = True, insert_query: bool = False, update_query: bool = False):
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)

                if update_query or insert_query:
                    print(f"Database Return Code: {result}")

                elif select_query:
                    result_list = []
                    for row in result:
                        result_list.append(dict(row))
                    return result_list

            except Exception as e:
                print(e)


class Vacancies(Base):

    __tablename__ = "vacancies"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    search_topic = Column(String)
    platform = Column(ForeignKey('platform.name'))
    company = Column(String)
    location = Column(String, nullable=True)
    date = Column(Date)
    url = Column(String)
    title = Column(String)

    def __init__(self, platform: str, search_topic: str, date: datetime, url: str, company: str, location: str,
                 title: str):
        self.platform = platform
        self.search_topic = search_topic
        self.date = date
        self.url = url
        self.company = company
        self.location = location
        self.title = title


class Platform(Base):

    __tablename__ = "platform"

    name = Column(String, primary_key=True)
    base_address = Column(String)

    def __init__(self, name: str, base_address: str):
        self.name = name
        self.base_address = base_address
