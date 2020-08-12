from application import app,bcrypt,db,mail
from flask import render_template,url_for,flash,redirect,request,abort
from application.forms import RegistrationForm,LoginForm,UpdateAccountForm,PostForm,ResetPasswordRequestForm,ResetPasswordForm
from application.models import User,Post
from flask_login import login_user,logout_user,current_user,login_required
import secrets
import os 
from PIL import Image
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page',1,type=int)
    posts = Post.objects.order_by('-date_posted').paginate(page=page,per_page=2)
    return render_template('home.html',posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password).save()
        flash(f'Account created for {user.username}!','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home')) 
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html',title='Login',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            random_hex = secrets.token_hex(8)
            _,f_ext = os.path.splitext(form.picture.data.filename)
            picture_fn = random_hex + f_ext
            picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)

            output_size = (125,125)
            i = Image.open(form.picture.data)
            i.thumbnail(output_size)
            i.save(picture_path)
            current_user.picture = picture_fn


        current_user.username = form.username.data 
        current_user.email = form.email.data 
        current_user.save()
        flash('Your account has been updated','success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',title='Account',form=form)

@app.route('/post/new',methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,user_created=current_user.id).save()
        current_user.posts.append(post)
        current_user.save()
        flash('Your post has been created successfully','success')
        return redirect(url_for('home'))
    return render_template('new_post.html',form=form,legend='Add new post')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.objects.get_or_404(post_id=post_id)
    return render_template('post.html',title=post.title,post=post)

@app.route('/post/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.objects.get_or_404(post_id=post_id)
    form = PostForm()
    if post.user_created != current_user:
        abort(403)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.save()
        flash('Your post has been updated!','success')
        return redirect(url_for('post',post_id=post.post_id))
    elif request.method=='GET':
        form.title.data = post.title
        form.content.data = post.content 

    return render_template('new_post.html',form=form,legend='Update post',title='Update post')

@app.route('/post/<int:post_id>/delete',methods=['GET','POST'])
@login_required
def delete_post(post_id):
    post = Post.objects.get_or_404(post_id=post_id)
    if post.user_created != current_user:
        abort(403)
    post.delete()
    flash('Your post has been deleted','success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.objects(username=username).first_or_404()
    posts = Post.objects(user_created=user).order_by('-date_posted').paginate(page=page,per_page=2)
    return render_template('user_posts.html',posts=posts,user=user)

@app.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        s = Serializer(app.config['SECRET_KEY'],'1800')
        token = s.dumps({'user_id':user.user_id}).decode('utf-8')
        msge = Message('Reset Password Request',sender='noreply@demo.com',recipients=[user.email])
        msge.body = f'''Please click this link to change password { url_for('reset_password',token=token,_external=True) }'''
        mail.send(msge)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    s = Serializer(app.config['SECRET_KEY'],'1800')
    try:
        user_id = s.loads(token)['user_id']
    except:
        user_id = None 
    if not(user_id):
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password_request'))
    user = User.objects(user_id=user_id).first()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        user.save()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html',form=form)

@app.errorhandler(404)
def error_404(e):
    return render_template('404.html'),404

@app.errorhandler(403)
def error_403(e):
    return render_template('403.html'),403

@app.errorhandler(500)
def error_500(e):
    return render_template('500.html'),500

