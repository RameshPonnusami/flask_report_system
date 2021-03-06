from app import app,db
from flask_report_system_models import FlaskReport,FlaskReportParameter,FlaskParameter,FlaskReportDataColor
from flask import render_template,request,url_for,redirect,make_response
import json
from sqlalchemy.sql import expression, functions
from sqlalchemy import types
from datetime import datetime, date
from decimal import *
import time

def default(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return "%.2f" % o

def get_model_columns(instance, exclude=[]):
    columns = instance.__table__.columns.keys()
    columns = list(set(columns) - set(exclude))
    return columns

def convert_object_into_dict( data, cols):
    return [{col: getattr(d, col) for col in cols} for d in data]

def queryset_to_dict(query_result):
    try:
        query_columns = query_result[0].keys()
        res = [list(ele) for ele in query_result]
        dict_list = [dict(zip(query_columns, l)) for l in res]
    except Exception as e:
        print(e)
        dict_list=[]
    return dict_list

@app.route('/',methods=['GET','POST'])
def home():
    return  render_template('flask_report_system/home.html')

@app.route('/create_flask_parameter',methods=['GET','POST'])
def flask_make_param():

    return "Created Successfully"

@app.route('/create_flask_report',methods=['GET','POST'])
def create_flask_report():
    #param: getting report details
    #retrun: add_report.html page with params
    if request.method=='POST':
        color_field_name = request.form.getlist('color_field_name')
        color_condition = request.form.getlist('color_condition')
        color = request.form.getlist('color')
        color_apply_level = request.form.getlist('color_apply_level')
        color_question = request.form.getlist('color_question')

        paramlist = request.form.getlist('selectedparam[]')
        reportname=request.form.get('reportname')
        reportType=request.form.get('reportType')
        reportSubType=request.form.get('reportSubType')
        reportCategory=request.form.get('reportCategory')
        description=request.form.get('description')
        sql=request.form.get('sql')
        report = FlaskReport(name=reportname,report_type=reportType,
                             report_sub_type=reportSubType,report_category=reportCategory,description=description,sql_query=sql)
        #Insert mapping data between report and params in  FlaskReportParameter
        for r in paramlist:
            param = FlaskReportParameter(parameter_id=r)
            report.params.append(param)
        db.session.add(report)
        #db.session.commit()
        db.session.flush()
        report_id=report.id
        print(report_id)
        if len(color_question)>1:
            for i, cf in enumerate(color_field_name):
                color_obj = FlaskReportDataColor(report_id=report_id, field_name=color_field_name[i], condition=color_condition[i],
                                                 color=color[i], apply_level=color_apply_level[i])
                db.session.add(color_obj)
            db.session.commit()
        db.session.commit()
        return redirect(url_for('edit_report_list'))
    ''' Concat not working in sqlite database '''
    # params=db.session.query(FlaskParameter.id,FlaskParameter.parameter_label,
    #                         FlaskParameter.parameter_name,functions.concat('${',expression.cast(FlaskParameter.parameter_name
    #                                                                                        ,types.Unicode),'}').label('parameter_full_name'))
    params=db.session.query(FlaskParameter.id,FlaskParameter.parameter_label,
                            FlaskParameter.parameter_name)

    return render_template("flask_report_system/add_report.html",params=params)

@app.route('/list_reports',methods=['GET','POST'])
def list_reports():
    params = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,
                              FlaskReport.report_type).filter(FlaskReport.is_active == True)
    return render_template('flask_report_system/list_report.html',params=params)

@app.route('/edit_report_list',methods=['GET','POST'])
def edit_report_list():
    params = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,
                              FlaskReport.report_type).filter(FlaskReport.is_active == True)
    return render_template('flask_report_system/edit_report_list.html',params=params)


@app.route('/flask_edit_report_details/<int:id>',methods=['GET','POST'])
def flask_edit_report_details(id):
    if request.method=='POST':
        print(request.form)
        color_field_name = request.form.getlist('color_field_name')
        color_condition = request.form.getlist('color_condition')
        color = request.form.getlist('color')
        color_apply_level = request.form.getlist('color_apply_level')
        color_question = request.form.getlist('color_question')

        paramlist = request.form.getlist('selectedparam[]')
        reportname = request.form.get('reportname')
        reportType = request.form.get('reportType')
        reportSubType = request.form.get('reportSubType')
        reportCategory = request.form.get('reportCategory')
        description = request.form.get('description')
        sql = request.form.get('sql')
        instance=FlaskReport.query.filter(FlaskReport.id == id)
        report=instance.update(dict(name=reportname, report_type=reportType,
                             report_sub_type=reportSubType, report_category=reportCategory, description=description,
                             sql_query=sql))
        db.session.commit()
        # Insert mapping data between report and params in  FlaskReportParameter
        FlaskReportParameter.query.filter_by(report_id=id).delete()
        db.session.commit()

        for r in paramlist:
            param = FlaskReportParameter(parameter_id=r,report_id=id)
            db.session.add(param)
        db.session.commit()
        FlaskReportDataColor.query.filter_by(report_id=id).delete()
        db.session.commit()
        cq= color_question if type(color_question)==int else len(color_question)
        if cq > 0:
            for  i,cf in enumerate(color_field_name):
                color_obj = FlaskReportDataColor( report_id=id,field_name=color_field_name[i],condition=color_condition[i],color=color[i],apply_level=color_apply_level[i])
                db.session.add(color_obj)
            db.session.commit()
        return  redirect(url_for('edit_report_list'))
    else:
        reportdetails = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,FlaskReport.report_type,
                                  FlaskReport.sql_query,FlaskReport.description).filter(FlaskReport.is_active == True,FlaskReport.id ==id ).first()
        report_param = db.session.query(FlaskParameter.parameter_display_type,FlaskParameter.parameter_format_type,
                                        FlaskParameter.parameter_label,
                                        FlaskParameter.parameter_name,
                                        FlaskParameter.parameter_sql,
                                        FlaskParameter.id,
                                        FlaskParameter.parent_id
                                        ).join(FlaskReportParameter,(FlaskReportParameter.parameter_id==FlaskParameter.id)).filter(
                                        FlaskReportParameter.report_id == id)
        report_color = db.session.query(FlaskReportDataColor.field_name,FlaskReportDataColor.condition,
                                        FlaskReportDataColor.color,FlaskReportDataColor.apply_level).filter(FlaskReportDataColor.report_id==id)

        reportdetails={"sql":reportdetails.sql_query,"name":reportdetails.name,"description":reportdetails.description,
                       "report_category":reportdetails.report_category,"report_type":reportdetails.report_type,"id":id}
        params = db.session.query(FlaskParameter.id, FlaskParameter.parameter_label,
                                  FlaskParameter.parameter_name
                                  )
        added_param=json.dumps(queryset_to_dict(report_param.all())) 
        added_color=json.dumps(queryset_to_dict(report_color.all()))
        return render_template('flask_report_system/edit_report.html', report=reportdetails,params=params,added_param=added_param,added_color=added_color)
@app.route('/flask_report_details/<int:id>',methods=['GET','POST'])
def flask_report_details(id):
    reportdetails = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,FlaskReport.report_type,
                              FlaskReport.sql_query).filter(FlaskReport.is_active == True,FlaskReport.id ==id ).first() #getting report details
    report_param = db.session.query(FlaskParameter.parameter_display_type,FlaskParameter.parameter_format_type,
                                    FlaskParameter.parameter_label,
                                    FlaskParameter.parameter_name,
                                    FlaskParameter.parameter_sql,
                                    FlaskParameter.id,
                                    FlaskParameter.parent_id
                                    ).join(FlaskReportParameter,(FlaskReportParameter.parameter_id==FlaskParameter.id)).filter(
                                    FlaskReportParameter.report_id == id).order_by(FlaskReportParameter.id) #getting report parameters
    listdict=[]
    paramereter_list=[] #store parameters name  as list alone
    paramereter_list_id=[]
    parent_id_list=[] #store parent id as list alone
    parent_id_listdict={}
    for rp in report_param: #iterating parameters for report
        dictv={}
        paramereter_list.append(rp.parameter_name)
        paramereter_list_id.append(rp.id)
        dictv['label']=rp.parameter_label
        dictv['display_type']=rp.parameter_display_type
        dictv['parameter_name']=rp.parameter_name
        if rp.parameter_display_type=='select' and (rp.parent_id is None or rp.parent_id==0):
            param_query=db.session.execute(rp.parameter_sql)
            param_result = param_query.fetchall()
            dictv['values']=param_result
        else:
            dictv['values'] =[]
        listdict.append(dictv)

        ##getting parent child params for requested report
        if rp.parameter_display_type == 'select' and rp.parent_id is not None:
            parent_id_list.append(rp.parent_id)
            if rp.parent_id in parent_id_listdict:
                if type(parent_id_listdict[rp.parent_id])==list:
                    parent_id_listdict[rp.parent_id].append(rp.id)
            else:
                parent_id_listdict[rp.parent_id]=[rp.id]
    parent_id_list = list(set(parent_id_list))


    # generating dropdown fields along with dependent dropdown configuration
    parent_params = []
    param_all_data=queryset_to_dict(report_param.all())
    if len(param_all_data)>1:
        for pid in parent_id_list:
            childlist=parent_id_listdict[pid]
            parentdict={}
            parentdict['parent_param_label']=[dictrow['parameter_name'] for dictrow in param_all_data if dictrow['id'] == pid][0]
            parentdict['parent_param_id']=pid
            parentdict['children']=[]
            if len(childlist)>0:
                for ch in childlist:
                    childict = {}
                    childict['child_param_label'] = [dictrow['parameter_name'] for dictrow in param_all_data if dictrow['id'] == ch][0]
                    childict['child_param_id'] = ch
                    parentdict['children'].append(childict)
            parent_params.append(parentdict)
    #return color condition
    colorcode = FlaskReportDataColor.query.filter(FlaskReportDataColor.report_id == id).all()
    color_cols = get_model_columns(FlaskReportDataColor)
    if colorcode is not None:
        color_data = convert_object_into_dict(colorcode, color_cols)
    else:
        color_data = []
    ##
    return render_template('flask_report_system/run_report.html',param=listdict,report_name=reportdetails.name,
                           plist=paramereter_list,report_id=id,plistid=paramereter_list_id,
                           parent_data=parent_params,color=color_data)


import time
@app.route('/run_report',methods=['GET','POST'])
def run_report():
    if request.method=='POST':
        time.sleep(5)
        report_id=request.form.get('report_id')
        plistid=request.form.getlist('plistid[]')
        plist_names=request.form.getlist('plist_names[]')
        reportdetails = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,FlaskReport.report_type,
                                  FlaskReport.sql_query).filter(FlaskReport.is_active == True,FlaskReport.id ==report_id ).first()


        exec_query=reportdetails.sql_query
        for pn in plist_names:
            #ex:${startDate}
            filterparam='${'+pn+'}'
            exec_query=exec_query.replace(filterparam,request.form.get(pn))

        try:
            result_query = db.session.execute(exec_query)
            # cursor.execute(role_query)
            columns_names = result_query._metadata.keys
            result_query = result_query.fetchall()
            queryset=queryset_to_dict(result_query)
            dataset = {"keys": columns_names, "data": queryset}
        except Exception as e:
            print(e)
            dataset={"keys":[],"data":[],"msg":" Error while processing! Contact your admin "+" Error is ==>"+str(e)}
        response=json.dumps(dataset,default=default)

        response = make_response(response)
        response.content_type = 'application/json'
        return make_response(response)


@app.route('/child_dropdown',methods=['GET','POST'])
def child_dropdown():
    if request.method == 'POST':

        parent_value=request.form.get('parent_value')
        parent_label=request.form.get('parent_label')
        child_param_id=request.form.get('child_param_id')
        child_param_label=request.form.get('child_param_label')
        report_param = db.session.query(FlaskParameter.parameter_display_type, FlaskParameter.parameter_format_type,
                                        FlaskParameter.parameter_label,
                                        FlaskParameter.parameter_name,
                                        FlaskParameter.parameter_sql,
                                        FlaskParameter.id,
                                        FlaskParameter.parent_id
                                        ).filter(FlaskParameter.id == child_param_id).first()
        exec_query=report_param.parameter_sql
        if report_param.parameter_display_type=='select':
            filterparam = '${' + parent_label + '}'
            exec_query = exec_query.replace(filterparam, parent_value)
            param_query=db.session.execute(exec_query)
            param_result = param_query.fetchall()
            child_list=[]
            for item in param_result:
                dict={}
                dict['value']=item[0]
                dict['label']=item[1]
                child_list.append(dict)
        data_dict={"child_dropdown_id":child_param_label,"data":child_list}
        return make_response(json.dumps(data_dict))

@app.route('/delete_report/<int:id>',methods=['GET','POST'])
def delete_report(id):
    try:
        FlaskReportParameter.query.filter_by(report_id=id).delete()
        db.session.commit()
    except Exception as e:
        print(e,'Error while deleting FlaskReportParameter')
    try:
        FlaskReport.query.filter_by(id=id).delete()
        db.session.commit()
    except Exception as e:
        print(e,'Error while deleting FlaskReport')
    return redirect(url_for('edit_report_list'))

@app.route('/param_data',methods=['GET','POST'])
def param_data():
    if request.method=='POST':
        print('post')
    if request.method == 'GET':
        print('GET')
        fp=FlaskParameter.query.all()
        cols=get_model_columns(FlaskParameter)
        fp=convert_object_into_dict(fp, cols)
        return render_template('flask_report_system/edit_param_list.html',fp=fp)

@app.route('/param_details/<int:id>',methods=['GET','POST'])
def param_details(id):
    if request.method == 'GET':
        fp = FlaskParameter.query.filter(FlaskParameter.id==id).first()
        parent_id=fp.parent_id
        fp={"parameter_name":fp.parameter_name,"parameter_label":fp.parameter_label,"parameter_sql":fp.parameter_sql,
             "description":fp.description,"parameter_display_type":fp.parameter_display_type,
             "parameter_format_type":fp.parameter_format_type,"parameter_default":fp.parameter_default,
             "parent_id":fp.parent_id,"id":fp.id}
        params = db.session.query(FlaskParameter.id, FlaskParameter.parameter_label,
                                  FlaskParameter.parameter_name)
        added_param = db.session.query(FlaskParameter.parameter_label,
                                        FlaskParameter.parameter_name,
                                        FlaskParameter.id).filter(FlaskParameter.id==parent_id).all()
        added_params=queryset_to_dict(added_param)
        return render_template('flask_report_system/edit_param.html',param=fp,params=params,added_params=added_params)

    if request.method == 'POST':
        print(request.form)
        paramlabel=request.form.get('paramlabel')
        parameter_name=request.form.get('parameter_name')
        paramdisplay_type=request.form.get('paramdisplay_type')
        paramformat_type=request.form.get('paramformat_type')
        description=request.form.get('description')
        parameter_sql=request.form.get('parameter_sql')
        parametervalue=request.form.get('parametervalue')
        parent_id=request.form.get('selectedparam[]')
        instance = FlaskParameter.query.filter(FlaskParameter.id == id)
        fp = {"parameter_name": parameter_name, "parameter_label": paramlabel,
              "parameter_sql": parameter_sql,
              "description": description, "parameter_display_type": paramdisplay_type,
              "parameter_format_type": paramformat_type,
              "parent_id": parent_id}
        param = instance.update(fp)
        db.session.commit()
        return redirect(url_for('param_data'))


@app.route('/add_parameter',methods=['GET','POST'])
def add_parameter():
    if request.method == 'POST':
        paramlabel = request.form.get('paramlabel')
        parameter_name = request.form.get('parameter_name')
        paramdisplay_type = request.form.get('paramdisplay_type')
        paramformat_type = request.form.get('paramformat_type')
        description = request.form.get('description')
        parameter_sql = request.form.get('parameter_sql')
        parametervalue = request.form.get('parametervalue')
        parent_id = request.form.get('selectedparam[]')
        param = FlaskParameter(parameter_name= parameter_name, parameter_label= paramlabel,
        parameter_sql= parameter_sql,
        description= description, parameter_display_type= paramdisplay_type,
        parameter_format_type= paramformat_type,
        parent_id= parent_id)
        db.session.add(param)
        db.session.commit()
        return redirect(url_for('param_data'))
    if request.method == 'GET':
        params = db.session.query(FlaskParameter.id, FlaskParameter.parameter_label,
                                  FlaskParameter.parameter_name)
        return render_template('flask_report_system/add_param.html',params=params)


@app.route('/delete_param/<int:id>',methods=['GET','POST'])
def delete_param(id):
    print('delete')
    FlaskParameter.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('param_data'))