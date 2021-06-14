from app import app, config
from flask import redirect, render_template, session, url_for, request
from app.database import SQLConnection

sqlconn = SQLConnection()

@app.route('/')
def home():
    return "hello world"