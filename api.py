from app import app,db
from models import FlaskReport,FlaskReportParameter,FlaskParameter
from flask import render_template,request,url_for,redirect,make_response
import json
def queryset_to_dict(query_result):
    query_columns = query_result[0].keys()
    res = [list(ele) for ele in query_result]
    dict_list = [dict(zip(query_columns, l)) for l in res]
    return dict_list

@app.route('/',methods=['GET','POST'])
def home():
    return "Welcome flask report home"

@app.route('/create_flask_parameter',methods=['GET','POST'])
def flask_make_param():

    return "Created Successfully"

@app.route('/create_flask_report',methods=['GET','POST'])
def flask_make_report():
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
    params=db.session.query(FlaskParameter.id,FlaskParameter.parameter_label)
    return render_template("add_report.html",params=params)

@app.route('/list_reports',methods=['GET','POST'])
def list_reports():
    params = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,
                              FlaskReport.report_type).filter(FlaskReport.is_active == True)
    return render_template('list_report.html',params=params)

@app.route('/flask_report_details/<int:id>',methods=['GET','POST'])
def flask_report_details(id):
    print(id,'flask_report_details')
    reportdetails = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,FlaskReport.report_type,
                              FlaskReport.sql_query).filter(FlaskReport.is_active == True,FlaskReport.id ==id ).first()
    print(reportdetails)
    report_param = db.session.query(FlaskParameter.parameter_display_type,FlaskParameter.parameter_format_type,
                                    FlaskParameter.parameter_label,
                                    FlaskParameter.parameter_name,
                                    FlaskParameter.parameter_sql,
                                    FlaskParameter.id
                                    ).join(FlaskReportParameter,(FlaskReportParameter.parameter_id==FlaskParameter.id)).filter(
                                    FlaskReportParameter.report_id == id)
    print(report_param)
    i=0
    listdict=[]
    paramereter_list=[]
    paramereter_list_id=[]
    for rp in report_param:
        dictv={}
        paramereter_list.append(rp.parameter_name)
        paramereter_list_id.append(rp.id)
        dictv['label']=rp.parameter_label
        dictv['display_type']=rp.parameter_display_type
        dictv['parameter_name']=rp.parameter_name
        if rp.parameter_display_type=='select':
            param_query=db.session.execute(rp.parameter_sql)
            param_result = param_query.fetchall()
            print('rp.parameter_sql',rp.parameter_sql,param_result)
            dictv['values']=param_result
        else:
            dictv['values'] =[]
        print(dictv)
        listdict.append(dictv)

    print(paramereter_list)
    return render_template('run_report.html',param=listdict,report_name=reportdetails.name,plist=paramereter_list,report_id=id,plistid=paramereter_list_id)



@app.route('/test_api',methods=['GET','POST'])
def test_api():
    if request.method=='POST':
        print(request.form)
        report_id=request.form.get('report_id')
        plistid=request.form.getlist('plistid[]')
        plist_names=request.form.getlist('plist_names[]')
        print(plistid)
        reportdetails = db.session.query(FlaskReport.id, FlaskReport.name,FlaskReport.report_category,FlaskReport.report_type,
                                  FlaskReport.sql_query).filter(FlaskReport.is_active == True,FlaskReport.id ==report_id ).first()
        print(reportdetails.sql_query)
        exec_query=reportdetails.sql_query
        for pn in plist_names:
            #ex:${startDate}
            filterparam='${'+pn+'}'
            print(pn,request.form.get(pn))
            exec_query=exec_query.replace(filterparam,request.form.get(pn))
            print(exec_query)

        result_query = db.session.execute(exec_query)
        # cursor.execute(role_query)
        columns_names = result_query._metadata.keys
        result_query = result_query.fetchall()
        queryset=queryset_to_dict(result_query)
        print(columns_names)
        dataset={"keys":columns_names,"data":queryset}
        return make_response(json.dumps(dataset))

