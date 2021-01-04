from app import app,manager
from models import *
from api import *

if __name__ == '__main__':
   app.secret_key = 'super secret key'
   app.session_cookie_name = 'ffff'
   app.config['SESSION_TYPE'] = 'filesystem'
   manager.run()  # debug=True
