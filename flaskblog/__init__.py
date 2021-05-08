from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import  Admin




app = Flask(__name__)
app.config['SECRET_KEY'] = '357575753rhh466246tgsdfgh4675'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


db=SQLAlchemy(app)


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


admin = Admin(app)



from flaskblog import routes
