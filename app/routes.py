import json
import numpy as np
from data_preprocessfile import*
import pickle

from flask_login import current_user, login_user, login_required, logout_user
from flask import flash, url_for, render_template, redirect, session, request, jsonify
from app.forms import (RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm)
from app.modelsdb import User, Post
from app import app, bcrypt, db, mail
from flask_mail import Message
from sklearn.preprocessing import MultiLabelBinarizer

#open json file "config.json" read mode
with open('config.json', 'r') as c:
    params=json.load(c)["params"]


######################create db module###########################
### User Database class
########################## End Database #####################################

###Open ML model pickle file in 'rb' mode for prediction the defect group and defect type
#model = pickle.load(open('finalized_model.sav', 'rb'))
# Hydrate the serialized objects.
with open('matdefecttypespred.pkl', 'rb') as f:
    multilabel_binarizers, classifiers = pickle.load(f)

################### Register form ##################
###Register page for new user ragistration
@app.route("/register", methods=['GET', 'POST'])
def register():
    #if user registered already then,
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #instance of form
    form = RegistrationForm()
    #if form are validate, then throw a alert massage 'success' .
    if form.validate_on_submit():
        #bcrypt: it use for protected the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #Creating a new user : pass all information from 'Form' to the database
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You are now able to log in!", 'success')
        #is user created an account then give him access to visite home page
        return redirect(url_for('login'))
    return render_template('register.html', _params=params, title='Register', form=form)

################## End Register ############################


############## Log in form for user #########################
###Log in page for user
@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    # if user  already login then,
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))

        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', _params=params, title='Login', form=form)

############### End Login form for user################################################
###Function for sending Email to user
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


###reset password form
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    #If user already exist
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #Create form
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', _params=params, title='Reset Password', form=form)

###Reset token with link reset_password
###reset password page
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:  ##if user had an invalid token or expired token, the return reset_request.html page
        flash('That is an invalid or expired token, please try with new on', 'warning')
        return redirect(url_for('reset_request'))
    ##if token is valid then display the reset password Form
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', _params=params, title='Reset Password', form=form)

###################### End reset password #####################################################################


################### Admin dashboard ###########################################################################
###dashboard page where admin can edit,delete , add a post
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required  #login required to access home page
def dashboard():
    if 'admin' in session and session['admin'] == params['admin_user']:
        post = Post.query.all()
        return render_template('dashboard.html', _params=params, post=post, title='dashboard')

    if request.method == 'POST':
        adminname = request.form.get('uname')
        adminpass = request.form.get('pass')
        if adminname == params['admin_user'] and adminpass == params['admin_password']:
            session['admin']=adminname
            post=Post.query.all()
            return render_template('dashboard.html', _params=params, post=post, title='dashboard')


    return render_template('adminlogin.html', _params=params, title='adminlogin')

### Post Edit for admin from dashboard
@app.route("/edit/<string:id>", methods=['GET', 'POST'])
def edit(id):
    if 'admin' in session and session['admin'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            slug = request.form.get('slug').strip()
            content = request.form.get('content')

            if id == '0':
                post = Post(title=box_title, slug=slug, content=content)
                db.session.add(post)
                db.session.commit()
            else:
                post=Post.query.filter_by(id=id).first()
                post.title = box_title
                post.slug = slug.strip()
                post.content = content
                db.session.commit()
                return redirect('/edit/'+id)
        post=Post.query.filter_by(id=id).first()
        return render_template('edit.html', id=id, _params=params, post=post, title='edit')


###Delete posst by admin from dashboard
@app.route("/delete/<string:id>", methods=['GET', 'POST'])
def delete(id):
    if 'admin' in session and session['admin'] == params['admin_user']:
        post=Post.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

###Search bar
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form=request.form
        search_value=form['search_string']
        search="%{0}%".format(search_value)
        result=Post.query.filter(Post.title.like(search)).all()
        return render_template('dashboard.html', post=result, _params=params, title='dashboard', legend="Search Result")
    else:
        return redirect('/dashboard')


### Log out admin from deshboard
@app.route("/adminlogout")
def adminlogout():
    session.pop('admin')
    return render_template('adminlogin.html', _params=params, title='adminlogin')

##################### End admin #######################################################

########################### Pages #####################################################
###home page
@app.route("/home")
@login_required #login required to access home page
def home():
    return render_template('home.html', _params=params, title='home')

### Show Post in about.html with next and previous button #############################
## About page
@app.route("/about", methods=['GET', 'POST'], defaults={"page": 1})
@app.route('/ <int:page>', methods=['GET', 'POST'])
@login_required #login required to access home page
def about(page):
    page = page
    pages = 4

    post = Post.query.order_by(Post.date_posted.desc()).paginate(page, pages, error_out=False)
    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        post = Post.query.filter(Post.title.like(search)).paginate(per_page=pages, error_out=False)
        return render_template('about.html', _params=params, title='about', post=post, tag=tag)

    return render_template('about.html', _params=params, title='about', post=post)


###post_slug link see all in about page
@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post=Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html', _params=params, post=post)



########################## End Show Post #############################
###logout route for logout user session.and back to login.html site
###logout for normal user
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#### after login user can see her /his account details
### Account Page
@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account', _params=params)

#####custom error handler page 404 if page not found!
@app.errorhandler(404)
def error404(error):
    return render_template('error.html', _params=params), 404

#Method error handler page 405 if method access is not allowed
@app.errorhandler(405)
def error405(error):
    return render_template('method_error.html', _params=params), 405

######################################## ML Model ########################################################
################################# Prediction the type from the ML Model ##################################
####route for predict data
@app.route('/predict', methods=['POST'])
@login_required #login required to do the prediction
def predict():
    '''
        For rendering results on HTML GUI
        '''
    #input 'heat_id' and 'mat_code' with --'weight' from home.html 'form'
    int_features = [x for x in request.form.values()]
    print(f"User Input features values :{int_features}")#

    #inputed 'heat_id' values from 'int_features[0]' set to a variable 'heatId'.
    heatId = int_features[0]
    print(f"User heatId[0] values :{heatId}")
    #inputed 'mat_code' with --'weight' values from 'int_features[1]' set to a variable in 'mat_list'.
    mat_list = int_features[1]
    print(f"User mat_list[1] code values :{mat_list}")

    #try and except for  invlaid input error handler
    try:
        final_features = testing_data(heatId, mat_list, recp)  # making the input features according to the feed of model
        print(f"heatId:{heatId}")
        print(f"mat_list: {mat_list}")
        print(f"Recp: {recp} \n")
        print(f"Final_features by def testing_data(heatId, mat_list, recp) :{final_features} \n")
        #predict DEFECT_Types from model
        mlb_predictions = classifiers.predict(final_features)
        print(f"Prediction by model.predict(final_features) :{mlb_predictions}")
        # Turn those classes into labels using the binarizer.
        classes = multilabel_binarizers.inverse_transform(mlb_predictions)
        print(f"Output Predicted result :{classes}")

        return render_template('home.html', _params=params,prediction_result=classes,  heatvalue=heatId, matweight=mat_list)
    except:
        return render_template('home.html', _params=params, prediction_error=params['predict_error'], heatvalue=heatId, matweight=mat_list)

##################### End Prediction ################

################## Api #################################################################
@app.route('/predict_api', methods=['POST'])
def predict_api():
    '''
    For direct API calls through request
    '''
    data = request.get_json(force=True)
    prediction = classifiers.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)