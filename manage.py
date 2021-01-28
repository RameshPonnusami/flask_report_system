from app import app,manager
from flask_report_system_models import *
from flask_report_system_api import *
try:
   db.create_all()
   db.session.commit()
except Exception as e:
   print(e)

if __name__ == '__main__':
   app.secret_key = 'super secret key'
   app.session_cookie_name = 'ffff'
   app.config['SESSION_TYPE'] = 'filesystem'
   manager.run()  # debug=True
