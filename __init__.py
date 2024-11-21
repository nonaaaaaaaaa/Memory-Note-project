from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
from sys import modules
from uuid import uuid4
from modules import *
import json
import os


users_module = Users()
memories_module = Memories()


app = Flask(__name__)

app.secret_key = 'pass@word#2044'


# Set session lifetime and Configure session to use secure cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = True


@app.before_request
def make_session_permanent():
    session.permanent = True

def load_user(func):
    """Decorator to load the user from the session"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_id = session.get('session_id')
        if session_id:
            user = users_module.get_user_by_session_id(session_id)
            if user:
                users_module.current_user = user
            else:
                users_module.current_user = {}
                session['session_id'] = None
        else:
            users_module.current_user = {}
        return func(*args, **kwargs)
    return wrapper

def is_authentication():
    """Check if the user is authenticated"""
    if users_module.current_user:
        return True
    else:
        return False