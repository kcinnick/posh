from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import database_exists, create_database


def create_product_table():
    engine = create_engine(
        "postgres:///nick:nickspassword@localhost/test:5432")
    if not database_exists(engine.url):
        create_database(engine.url)
    connection = engine.connect()

    db_session = scoped_session(sessionmaker(
        autocommit=False, autoflush=True, bind=engine))
    query = "create table if not exists product ("
    query += " URL VARCHAR(355) PRIMARY KEY,"
    query += " POSTED_AT TIMESTAMP,"
    query += " OWNER VARCHAR(100),"
    query += " BRAND VARCHAR(100),"
    query += " PRICE DECIMAL,"
    query += " SIZE VARCHAR(30),"
    query += " LISTING_ID VARCHAR(200),"
    query += " TITLE VARCHAR(355),"
    query += " PICTURES TEXT,"
    query += " DESCRIPTION TEXT,"
    query += " COLORS TEXT,"
    query += " COMMENTS TEXT,"
    query += " BUILT_FROM VARCHAR(4)"
    query += ")"
    db_session.execute(query)


def main():
    create_product_table()


if __name__ == '__main__':
    main()
