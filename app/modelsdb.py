from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager, app

###Make user session.
from flask_login import UserMixin

###Load user id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):#for username,email,password
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


    ####Reset token , expired of this token,
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    ###Verify token
    @staticmethod
    def verify_reset_token(token):
        #Create a Serializer
        s = Serializer(app.config['SECRET_KEY'])
        try:#Load the token according to user
            user_id = s.loads(token)['user_id']
        except:
            return None
        #if no execption then return the user with user_id
        return User.query.get(user_id)

    def __repr__(self):#how object can printed
        return f"User('{self.username}', '{self.email}')"



###Post database class for post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):#Print post
        return f"Post('{self.title}','{self.slug}', '{self.date_posted}')"

###Created Database site.db file
##db.create_all()
##db.session.commit()

