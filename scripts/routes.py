from flask import render_template, url_for, flash, redirect, request
from scripts import app, db, bcrypt
from scripts.forms import RegistrationForm, LoginForm
from scripts.models import User, Post
from werkzeug import secure_filename
from flask_login import login_user, current_user, logout_user, login_required
from flask_uploads import UploadSet, configure_uploads, IMAGES
import string
import random
from azure.storage.blob import BlockBlobService

from load import *
import numpy as np
import argparse
import sys
import time
from werkzeug import secure_filename
import tensorflow as tf
import re
import sys
import os
sys.path.append(os.path.abspath("./model"))

global model, graph, label

model_file = "data/retrained_graph.pb"
label_file = "data/retrained_labels.txt"
input_height = 224
input_width = 224
input_mean = 128
input_std = 128
input_layer = "input"
output_layer = "final_result"
input_name = "import/" + input_layer
output_name = "import/" + output_layer

graph, label = init(model_file, label_file)
input_operation = graph.get_operation_by_name(input_name)
output_operation = graph.get_operation_by_name(output_name)


photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = '.'
configure_uploads(app, photos)


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")

@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
@login_required
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST' and 'photo' in request.files:
        #filename = photos.url(request.files['photo'])
        #fil = request.files['photo']
        #return render_template('index2.html')
        #return 'text'
        model_file = "data/retrained_graph.pb"
        label_file = "data/retrained_labels.txt"
        input_height = 224
        input_width = 224
        input_mean = 128
        input_std = 128
        input_layer = "input"
        output_layer = "final_result"
        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        graph, label = init(model_file, label_file)

        input_operation = graph.get_operation_by_name(input_name)
        output_operation = graph.get_operation_by_name(output_name)

        filename = photos.save(request.files['photo'])
        #os.rename('./'+filename, './'+'output.png')

 
        t = read_tensor_from_image_file(filename, input_height=input_height,
                                        input_width=input_width, input_mean=input_mean, input_std=input_std)

        with tf.Session(graph=graph) as sess:
            start = time.time()
            results = sess.run(output_operation.outputs[0],
                               {input_operation.outputs[0]: t})
            end = time.time()

        results = np.squeeze(results)

        top_k = results.argsort()[-5:][::-1]

        #labels = load_labels(label_file)

        #print('\nEvaluation time (1-image): {:.3f}s\n'.format(end-start))
        #template = "{} (score={:0.5f})"
        name = []
        text = []
        for i in top_k:
            #print(template.format(labels[i], results[i]))
            name.append(label[i])  
            text.append(results[i])  

        return render_template("index.html", s1=name[0], s2=text[0], s3=name[1], s4=text[1], s5=name[2], s6=text[2])

    return render_template('index.html')


