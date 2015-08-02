#!/usr/bin/env python
from pyapi import Pyapi
from flask import Flask, request, send_from_directory
import os
from redis import Redis
from hashlib import md5
from random import randint
import datetime

redis = Redis()

@Pyapi.route('/')
def index():
    name = request.args.get('name', 'World')
    return "Hello, {0}!".format(name)

@Pyapi.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(Pyapi.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@Pyapi.route('/v1/auth', methods=['POST', 'GET'])
def auth():
    email = request.args.get('email','')
    if not email:
        return "An Email is required to Authenticate"
    if request.method == 'POST':
        token = md5("{0}{1}".format(email,randint(0,20000))).hexdigest()
        redis.setex("token:{0}".format(email), token, (3600*2))
        redis.setex(token, 'True', (3600*2))
        return "Your Token is valid for 2 hours: {}".format(token)
    token = redis.get("token:{0}".format(email))
    if token == None:
        return "Please authenticate via POST with your email"
    return 'Your token is {0}'.format(token) 

@Pyapi.route('/v1/validate')
def token():
    token = request.args.get('token','')
    if not token:
        return "Please specify a token to validate"
    return "{}".format(redis.get(token))

@Pyapi.route('/v1/time')
def time():
    token = request.args.get('token','')
    if not token:
        return "Please specify a token to validate"
    if not redis.get(token):
        return "Your token doesn't appear to be valid"
    return "The Time is {}".format(datetime.datetime.utcnow())
