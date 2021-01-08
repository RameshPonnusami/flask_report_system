from app import app,db
from models import FlaskReport,FlaskReportParameter,FlaskParameter
from flask import render_template,request,url_for,redirect,make_response
import json
from sqlalchemy.sql import expression, functions
from sqlalchemy import types

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
    return  render_template('home.html')

@app.route('/create_flask_parameter',methods=['GET','POST'])
def flask_make_param():

    return "Created Successfully"

@app.route('/create_flask_report',methods=['GET','POST'])
def create_flask_report():
    #param: getting report details
    #retrun: add_report.html page with params
    if request.method=='POST':
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
        db.session.commit()
    params=db.session.query(FlaskParameter.id,FlaskParameter.parameter_label,
                            FlaskParameter.parameter_name,functions.concat('${',expression.cast(FlaskParameter.parameter_name
                                                                                           ,types.Unicode),'}').label('parameter_full_name'))
    return render_template("add_report.html",params=params)

@app.route('/list_reports',methods=['GET','POST'])
def list_reports():
    params = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,
                              FlaskReport.report_type).filter(FlaskReport.is_active == True)
    return render_template('list_report.html',params=params)

@app.route('/edit_report_list',methods=['GET','POST'])
def edit_report_list():
    params = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,
                              FlaskReport.report_type).filter(FlaskReport.is_active == True)
    return render_template('edit_report_list.html',params=params)


@app.route('/flask_edit_report_details/<int:id>',methods=['GET','POST'])
def flask_edit_report_details(id):
    if request.method=='POST':
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

        reportdetails={"sql":reportdetails.sql_query,"name":reportdetails.name,"description":reportdetails.description,
                       "report_category":reportdetails.report_category,"report_type":reportdetails.report_type,"id":id}
        params = db.session.query(FlaskParameter.id, FlaskParameter.parameter_label,
                                  FlaskParameter.parameter_name,
                                  functions.concat('${', expression.cast(FlaskParameter.parameter_name
                                                                         , types.Unicode), '}').label(
                                      'parameter_full_name'))
        added_param=json.dumps(queryset_to_dict(report_param.all()))
        return render_template('edit_report.html', report=reportdetails,params=params,added_param=added_param)
@app.route('/flask_report_details/<int:id>',methods=['GET','POST'])
def flask_report_details(id):
    reportdetails = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,FlaskReport.report_type,
                              FlaskReport.sql_query).filter(FlaskReport.is_active == True,FlaskReport.id ==id ).first()
    report_param = db.session.query(FlaskParameter.parameter_display_type,FlaskParameter.parameter_format_type,
                                    FlaskParameter.parameter_label,
                                    FlaskParameter.parameter_name,
                                    FlaskParameter.parameter_sql,
                                    FlaskParameter.id,
                                    FlaskParameter.parent_id
                                    ).join(FlaskReportParameter,(FlaskReportParameter.parameter_id==FlaskParameter.id)).filter(
                                    FlaskReportParameter.report_id == id)
    listdict=[]
    paramereter_list=[]
    paramereter_list_id=[]

    parent_id_list=[]
    parent_id_listdict={}
    for rp in report_param:
        dictv={}
        paramereter_list.append(rp.parameter_name)
        paramereter_list_id.append(rp.id)
        dictv['label']=rp.parameter_label
        dictv['display_type']=rp.parameter_display_type
        dictv['parameter_name']=rp.parameter_name
        if rp.parameter_display_type=='select' and rp.parent_id is None:
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


    print(parent_id_listdict)
    parent_params = []
    param_all_data=queryset_to_dict(report_param.all())
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

    return render_template('run_report.html',param=listdict,report_name=reportdetails.name,
                           plist=paramereter_list,report_id=id,plistid=paramereter_list_id,
                           parent_data=parent_params)



@app.route('/run_report',methods=['GET','POST'])
def run_report():
    if request.method=='POST':

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


        result_query = db.session.execute(exec_query)
        # cursor.execute(role_query)
        columns_names = result_query._metadata.keys
        result_query = result_query.fetchall()
        queryset=queryset_to_dict(result_query)
        dataset={"keys":columns_names,"data":queryset}
        return make_response(json.dumps(dataset))


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
