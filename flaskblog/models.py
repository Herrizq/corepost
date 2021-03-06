from datetime import datetime
from flaskblog import db, login_manager,app, admin
from flask_login import UserMixin,current_user
from flask_admin.contrib.sqla import ModelView





followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password =  db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post',backref='author',lazy=True)
    about = db.Column(db.Text(),default="Kiedyś to uzupełnie")
    role = db.Column(db.Text(), default ="user")
    is_verified = db.Column(db.Text(),default = "no")
    __searchable__ = ['username']
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0



    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"





class Post(db.Model):
    id =db.Column(db.Integer, primary_key = True)

    date_posted = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)
    content = db.Column(db.Text(10),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)
    tag = db.Column(db.String(),default="#hello")
    post_pic = db.Column(db.String())


    def __repr__(self):
        return f"Post('{self.date_posted}')"

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role =='admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Post,db.session))
