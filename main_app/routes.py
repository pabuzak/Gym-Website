import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from main_app import app, db, bcrypt, mail
from main_app.forms import (RegistrationForm, LoginForm,
                            UpdateAccountForm, PostForm,
                            RequestResetForm, ResetPasswordForm)
from main_app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


# Routes

# Route for homepage
@app.route("/")  # Route to main page
@app.route("/home/")  # Route to home page
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)
    # call to render the home page template


# Route for about page
@app.route("/about")
def about():
    return render_template('about.html', title='About')
    # call to render aboout page template


# Route for registration page
@app.route("/register", methods=['Get', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        # call to redirect home
    form = RegistrationForm()
    if form.validate_on_submit():
        # generate hashtag password
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        # user username, email, password
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # flash message
        flash('Your account has been created! You are now able to log in',
              'success')
        return redirect(url_for('login'))
        # call to redirect login
    return render_template('register.html', title='Register', form=form)
    # call to render register page template


# Route for login page
@app.route("/login", methods=['Get', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        # call to redirect home
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            # remember user
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('home'))
            # call to redirect next page or home
        else:
            # flash message
            flash('Login Unsuccessful. Please check your email and password',
                  'danger')
    return render_template('login.html', title='Login', form=form)
    # call to render login pages


# Route for login out
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
    # call to redirect home


# processes profile picture
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # picture path to static folder
    picture_path = os.path.join(app.root_path,
                                'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # save picture path
    i.save(picture_path)
    return picture_fn
    # return picture


# Route for account page
@app.route("/account", methods=['Get', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # save picture
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        # flash message
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
        # call to redirect account
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
    # call to render account pages


# Route for new posts
@app.route("/post/new", methods=['Get', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # post title and content data
        post = Post(title=form.title.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html',
                           title='New Post', form=form, legend='New Post')
    # call to render create post pages


# Route for individual posts
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)
    # call to render post pages


# Route for update/delete posts
@app.route("/post/<int:post_id>/update", methods=['Get', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        # post title data
        post.title = form.title.data
        # post content data
        post.content = form.content.data
        db.session.commit()
        # flashh masage
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        # post title data
        form.title.data = post.title
        # post content data
        form.content.data = post.content
    return render_template('create_post.html',
                           title='Update Post', form=form,
                           legend='Update Post')
    # call to render create post page


# Route for deleting posts
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # post id
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    # delete post
    db.session.delete(post)
    db.session.commit()
    # flash message
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
    # call to redirect home


# send reset email
def send_reset_email(user):
    # get reset token to user
    token = user.get_reset_token()
    # message for reset request
    msg = Message('Password Reset Request',
                  sender='admin@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then ignore this email
 and no changes will be made.
'''
    mail.send(msg)
    # send message to mail


# Route for reset_request
@app.route("/reset_password", methods=['Get', 'POST'])
# Route to reset_password
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        # call to redirect home
    form = RequestResetForm()
    if form.validate_on_submit():
        # email data
        user = User.query.filter_by(email=form.email.data).first()
        # send email reset
        send_reset_email(user)
        # flash message
        flash('An email has been sent with instructions'
              'to reset your password.', 'info')
    return redirect(url_for('login'))
    # call to redirect login
    return render_template('reset_request.html',
                           title='Reset Password', form=form)
    # call to render reset request page


# Route for reset_password
@app.route("/reset_password/<token>", methods=['Get', 'POST'])
# Route to reset_password
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        # call to redirect home
    user = User.verify_reset_token(token)
    if user is None:
        # flash message
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # genereate password hashtags
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        # user password to hashed password
        user.password = hashed_password
        db.session.commit()
        # flash message
        flash('Your password has been updated!'
              'You are now able to log in', 'success')
        return redirect(url_for('login'))
        # call to redirect to login
    return render_template('reset_token.html',
                           title='Reset Password', form=form)
    # call to render reset token page
