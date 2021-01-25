from sqlalchemy.dialects.postgresql import UUID,JSON
from sqlalchemy.sql import func
from datetime import datetime
from app import db
import uuid
import json
#from flask_simple_serializer.serializers import Serializer
from datetime import date ,datetime

class FlaskReport(db.Model):
    __tablename__='flask_report'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String(100),nullable=False)
    sql_query=db.Column(db.Text(),nullable=False)
    is_active =db.Column(db.Boolean(), nullable=False,default=True)
    description =db.Column(db.String(1000),nullable=False)
    report_type =db.Column(db.String(15),nullable=False,default='Table')
    report_sub_type =db.Column(db.String(15),nullable=False,default='Table')
    report_category =db.Column(db.String(15),nullable=False,default='OFFICE')
    created_at = db.Column(db.DateTime(timezone=True), index=True, server_default=func.now())
    params = db.relationship('FlaskReportParameter')

class FlaskParameter(db.Model):
    __tablename__='flask_parameter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parameter_name = db.Column(db.String(100),nullable=False)
    parameter_label = db.Column(db.String(100),nullable=False)
    parameter_sql = db.Column(db.Text(),nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    parameter_display_type = db.Column(db.String(50), nullable=False)
    parameter_format_type = db.Column(db.String(50), nullable=False)
    parameter_default = db.Column(db.String(45), nullable=True)
    parent_id = db.Column(db.Integer,nullable=True)
    reportparams = db.relationship('FlaskReportParameter')



class FlaskReportParameter(db.Model):
    __tablename__='flask_report_parameter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_id = db.Column(db.Integer(), db.ForeignKey('flask_report.id'))
    parameter_id = db.Column(db.Integer(), db.ForeignKey('flask_parameter.id'))

import enum
class ApplyColorEnum(enum.IntEnum):
    complete_row = 1
    only_column = 2
class FlaskReportDataColor(db.Model):
    __tablename__='flask_report_data_color'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_id = db.Column(db.Integer(), db.ForeignKey('flask_report.id'))
    field_name= db.Column(db.String(50),nullable=True)
    condition= db.Column(db.String(200),nullable=True)
    color= db.Column(db.String(20),nullable=True)
    apply_level = db.Column(db.Integer(),default=1,nullable=True)

