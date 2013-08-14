#!/usr/bin/env python

import flask
import json
from logparser import fetchlogs
from werkzeug.contrib.cache import SimpleCache
from werkzeug import secure_filename
import os

# Create the application
APP = flask.Flask(__name__)
APP.config.from_pyfile('logview_config.py')
print APP.config
# APP.config.from_envvar('LOFVIEW_CONFIG', silent=True)

# Creating the Cache Object
cache = SimpleCache(default_timeout=3600)

# Log Saving Directory
log_directory = APP.config['LOG_UPLOAD']
ALLOWED_EXTENSIONS = APP.config['ALLOWED_EXTENSIONS']

# Function which verify extension of the file
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


@APP.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if flask.request.method == 'POST':
        if flask.request.form['username'] != APP.config['USERNAME']:
            error = 'Invalid username'
        elif flask.request.form['password'] != APP.config['PASSWORD']:
            error = 'Invalid password'
        else:
            flask.session['logged_in'] = True
            flask.flash('You were logged in')
            return flask.redirect(flask.url_for('index'))
    return flask.render_template('login.html', error=error)


@APP.route('/logout')
def logout():
    flask.session.pop('logged_in', None)
    flask.flash('You were logged out')
    return flask.redirect(flask.url_for('login'))


@APP.route('/')
def index():
    """
    Displays the index page accessible at '/'
    """
    if not flask.session.get('logged_in'):
        flask.abort(401)
    log_hash_table = {}
    fh = open('/var/tmp/logviewer/log.json', 'r')
    log_hash_table = json.load(fh)
    fh.close()
    cache.clear()
    if not cache.get('data'):
        cache.set('data', log_hash_table)
    return flask.render_template('index.html', log_hash_table=cache.get('data'))


@APP.route('/upload', methods=['GET','POST'])
def upload():
    if not flask.session.get('logged_in'):
        flask.abort(401)
    if flask.request.method == 'POST':
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        upload_file = flask.request.files['file']
        if upload_file and allowed_file(upload_file.filename):
            filename = secure_filename(upload_file.filename)
            upload_file.save(os.path.join(log_directory, filename))
            flask.flash('Your file uploaded successfully')
            if fetchlogs.fetch_logs(log_path=log_directory):
                return flask.redirect(flask.url_for('index'))
    else:
        flask.flash('Looks like post method is not used or there may \
                be issue with the file')
        return flask.render_template('upload.html')


@APP.route('/log/<log_id>')
def json_file(log_id):
    """
    Displays Json format of the files '/'
    """
    if not flask.session.get('logged_in'):
        flask.abort(401)
    hash_table_object = cache.get('data')
    content = hash_table_object[log_id]['content']
    return flask.render_template('json_file.html', content=content)

if __name__ == '__main__':
    APP.debug = True
    APP.run()

"""
for root, directory, files in os.walk(log_directory_path):
        for log_file in files:
            file_absoulte_path = os.path.join(root, log_file)
            st =  os.stat(file_absoulte_path)
            log_data = [st.st_size, st.st_mtime, log_file]
            log_hash_table[file_absoulte_path] = log_data

    log_url = APP.config['LOG_URL']
    fetchlogs.fetch_logs(log_url)
"""
