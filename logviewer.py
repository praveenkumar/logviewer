#!/usr/bin/env python

import flask
import os
import json
from logparser import fetchlogs
from werkzeug.contrib.cache import SimpleCache

# Create the application
APP = flask.Flask(__name__)
APP.config.from_pyfile('logview_config.py')
print APP.config
#APP.config.from_envvar('LOFVIEW_CONFIG', silent=True)

# Creating the Cache Object
cache = SimpleCache(default_timeout = 3600)


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
    fh = open('/var/tmp/logviewer/log.json','r')
    log_hash_table = json.load(fh)
    fh.close()
    if not cache.get('data'):
        cache.set('data', log_hash_table)
    return flask.render_template('index.html', log_hash_table=cache.get('data')) 

@APP.route('/upload')
def upload():
    return flask.render_template('upload.html')

@APP.route('/log/<log_id>')
def json_file(log_id):
    
    """
    Displays Json format of the files '/'
    """
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