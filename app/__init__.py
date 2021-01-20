
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


###AppStart
#from app.modelsdb import User
app = Flask(__name__)

#Set secret key :its protect against modifying cookies & cross-site request forgery attacks
####app.secret_key = 'super-secret-key-XYZABCD':import secrets, secrets.token_hex(16)
app.config['SECRET_KEY']='e6384f8e584848dde42c1ea66df065d0'

############################# Database ######################################
###sqlite:set configaration:site.db should be create in model directory alongside in python module
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finalversion_22.db'

##Xampp database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/mlprojectdb'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://rahimsajjad@sqldatabaseforapp:dummy_PW.8642@sqldatabaseforapp.mysql.database.azure.com/mlprojectdb'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://rahim@servernameishope:dummy_PW.8642@servernameishope.mysql.database.azure.com/mluserpost'


###Create SQLALCHEMY database instance
db=SQLAlchemy(app)
###Pass app into all extension
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



###For email to set forget get password
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kiteblogs@gmail.com'
app.config['MAIL_PASSWORD'] = 'Rahim0167'
mail = Mail(app)

from app import routes
###Load routes.py

