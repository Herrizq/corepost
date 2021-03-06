from flask import render_template,url_for, flash, redirect,request, abort
from flaskblog import app, db,bcrypt
from flaskblog.forms import RegistrationForm, LoginForm,UpdateAccountForm, PostForm, EmptyForm
from flaskblog.models import User, Post
from flask_login import login_user,current_user,logout_user,login_required
import secrets
import os
from PIL import Image



@app.route("/")
@app.route("/home")
def home():
	posts = Post.query.all()
	return render_template('home.html', posts=posts)


@app.route("/about")
def about():
	return render_template('about.html',title='About')

@app.route("/register",methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email = form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in','success')
		return redirect(url_for('login'))
	return render_template('register.html', title ='Register', form=form)

@app.route("/login",methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unseccessful. Please check email and password','danger')
	return render_template('login.html', title ='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex +f_ext
	picture_path = os.path.join(app.root_path, 'static', picture_fn)

	output_size = (125,125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path)
	prev_picture = os.path.join(app.root_path, 'static', current_user.image_file)
	if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'default.jpg':
		os.remove(prev_picture)
	return picture_fn






@app.route("/account",methods=['GET','POST'])
@login_required
def account():
	image_file =url_for('static',filename=current_user.image_file)
	form=UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.about = form.about.data
		db.session.commit()
		flash('Your Account Has Been Updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.about.data = current_user.about
	return render_template('account.html',title='account',image_file=image_file, form=form)

def save_pic(form_pic):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_pic.filename)
	pic_fn = random_hex +f_ext
	pic_path = os.path.join(app.root_path, 'static', pic_fn)

	output_size = (420,220)
	i = Image.open(form_pic)
	i.thumbnail(output_size)

	i.save(pic_path)

	return pic_fn

@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():

	form = PostForm()

	if form.validate_on_submit():
		post= Post(content=form.content.data, author=current_user, tag=form.tag.data, post_pic = form.pic.data)
		if form.pic.data:
			picture_file = save_pic(form.pic.data)
			post.post_pic = picture_file

		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', form=form, legend = 'New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title='Post', post=post)

@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form =PostForm()
	if form.validate_on_submit():
		post.content=form.content.data
		post.tag=form.tag.data
		db.session.commit()
		flash('Your post has been updated', 'success')
		return redirect(url_for('home', post_id=post_id))
	elif request.method =='GET':
		form.content.data = post.content
		form.tag.data = post.tag
	return render_template('create_post.html', title='Update Post', form=form, legend = 'Update Post')




@app.route("/user/<username>")
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.all()
	form = EmptyForm()

	return render_template('post_author_page.html', user=user, posts=posts, form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found.'.format(username),'danger')
			return redirect(url_for('index'))
		if user == current_user:
			flash('You cannot follow yourself!','danger')
			return redirect(url_for('user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash('You are following {}!'.format(username),'success')
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('home'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found.'.format(username),'danger')
			return redirect(url_for('index'))
		if user == current_user:
			flash('You cannot unfollow yourself!','danger')
			return redirect(url_for('user', username=username))
		current_user.unfollow(user)
		db.session.commit()
		flash('You are not following {}.'.format(username),'danger')
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('home'))


@app.route("/post/<post_tag>")
def post_tag_page(post_tag):
	forms= PostForm()
	user = Post.query.filter_by(tag=post_tag).first()
	posts = Post.query.all()
	form = EmptyForm()

	return render_template('tag_posts.html',user=user, posts=posts, form=form, forms=forms)


@app.route("/search", methods=['GET','POST'])
def search_user():
	form = EmptyForm()
	if request.method =='POST':
		form = request.form
		search_value=form['search_string']
		users_list=User.query.all()
		results=User.query.filter_by(username=search_value).first()


	return render_template('search_user.html', results=results, form=form,search_value=search_value,users_list=users_list)
