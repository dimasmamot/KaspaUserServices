import os
import json
import string
import random
from bson import json_util
from flask import make_response

def root_dir():
    return os.path.dirname(os.path.abspath(__file__))

def nice_json(arg):
    response = make_response(json.dumps(arg, sort_keys=True, indent=4, default=json_util.default))
    response.headers['Content-type'] = "application/json"
    return response

def generate_random(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def raise_json_code(code, message):
    jsonStructure = {
        "code" : code,
        "message" : message 
    }
    return jsonStructure

def raise_json_code_with_data(code, message, data):
    jsonStructure = {
        "code" : code,
        "message" : message,
        "data" : data
    }
    return jsonStructure