from config import db_uri
from sqlalchemy import text
import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine(db_uri)
create_table_query='CREATE TABLE office(id int,name varchar(30));'
insert_data_query=''' insert into office(id,name)values(1,'Head Office'),(2,'Branch Office'); '''
query_list=[create_table_query,insert_data_query]
for q in query_list:
    engine.execute(q)