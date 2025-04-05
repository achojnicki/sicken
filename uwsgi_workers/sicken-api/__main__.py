from api import API
from flask import Flask, request

api=API()
application=Flask(__name__)
application.config['TRAP_HTTP_EXCEPTIONS']=True

@application.route('/<destination>',methods=['POST'])
def router(destination):
    return api.router(destination, request.form, request)


@application.errorhandler(Exception)
def error_handler(error):
    return api.error(error)