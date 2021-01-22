from config import db_uri
from sqlalchemy import text
import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine(db_uri)
create_table_query=['CREATE TABLE office_example(id int,name varchar(30));',
                    ' CREATE TABLE department_example(id int,name varchar(30),office_id int);',
                    'create table employee_example(id int,name varchar(20),department_id int);']
insert_data_query=[''' insert into office_example(id,name)values(1,'Head Office'),(2,'Branch Office'); ''',
                   ''' insert into department_example(id,name,office_id)values(1,'Business',1),(2,'IT',1),(3,'Admin',2);''',
                   ''' INSERT into employee_example(id,name,department_id)values(1,'Ramesh',1),(2,'Ponnusamy',1),(3,'Senthil',2),(4,'Bharath',3) ''',
                   ''' INSERT INTO flask_parameter
                    (parameter_name, parameter_label, parameter_sql, description, parameter_display_type, 
                    parameter_format_type, parameter_default, parent_id)
                    VALUES('selectDate', 'Select Date', '', 'Select Date From Datepicker When Run The Report',
                     'date', 'date', '', null);
                     ''']

query_list=[create_table_query,insert_data_query]
for q in create_table_query:
    engine.execute(q)
for q in insert_data_query:
    engine.execute(q)