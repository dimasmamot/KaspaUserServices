import json

from bson import json_util

from flask import request

from app import app
from app.models import User, Sensor, Topic

from pymodm.errors import ValidationError
from pymongo.errors import DuplicateKeyError

from app.utils import nice_json, raise_json_code, raise_json_code_with_data

@app.route("/", methods=["GET"])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "listusers": "/api/v1/users",
            "user": "/api/v1/users/<email>",
            "register": "/api/v1/users/register",
            "login": "/api/v1/users/login",
            "addsensor": "/api/v1/users/addsensor",
            "get_sensor": "/api/v1/users/<email>/sensors",
            "get_one_sensor": "/api/v1/users/<email>/<sensorname>"
        }
    })

@app.route("/api/v1/users", methods=["GET"])
def user_list():
    listUser = {
        "user" : []
    }
    try:
        allUser = User.objects.all()
    except User.DoesNotExist:
        return nice_json(raise_json_code(400, "User Empty"))
    
    for user in allUser:
        listUser['user'].append(user.to_son().to_dict())
    
    return nice_json(listUser)

@app.route("/api/v1/users/<email>", methods=["GET"])
def user_record(email):
    try:
        oneUser = User.objects.get({'_id' : email})
    except User.DoesNotExist:
        return nice_json(raise_json_code(400, "User Not Found"))
    
    return nice_json(raise_json_code_with_data(200, "OK", oneUser.to_son().to_dict())) 

@app.route("/api/v1/users/register", methods=["GET","POST"])
def register():
    if request.is_json:
        req_data = request.get_json()
        try:
            usernameData = req_data["username"]
            passwordData = req_data["password"]
            emailData = req_data["email"]
        except Exception as err:
            print("[Error] : {}".format(err))
            return nice_json(raise_json_code(400, "Variable Error, Please Fill All the Field"))
        
        try:
            user = User(
                email=emailData, 
                username=usernameData
            )
            user.set_password(passwordData)
            user.save(force_insert=True)
        except ValidationError as ve:
            print("[Error] : {}".format(ve.message))
            return nice_json(raise_json_code(400, "Paramter Not Valid"))
        except DuplicateKeyError:
            print("[Error] : Duplicate email")
            return nice_json(raise_json_code(400, "There is already user with that email address."))

        return nice_json(raise_json_code(200, "Successfully Registered"))            
        
    else:
        return nice_json(raise_json_code(400, "Please send proper request in json"))

@app.route("/api/v1/users/login", methods=["POST"])
def login():
    if request.is_json:
        req_data = request.get_json()
        try:
            emailData = req_data["email"]
            passwordData = req_data["password"]
        except Exception as err:
            print("[Error] : {}".format(err))
            return nice_json(raise_json_code(400, "Variable Error, Please Fill All the Field"))

        try:
            user = User.objects.get({'_id':emailData})
        except User.DoesNotExist:
            return nice_json(raise_json_code(400, "Wrong Email/Password"))

        try:
            if user.check_password_hash(passwordData):
                return nice_json(raise_json_code(200, "Logged In"))
            else:
                return nice_json(raise_json_code(400, "Log In Failed"))
        except Exception as err:
            print("[Error] : {}".format(err))
            return nice_json(raise_json_code(400, "Bad Password"))
    else:
        return nice_json(raise_json_code(400, "Please Send Proper JSON Request"))
        
@app.route("/api/v1/users/addsensor", methods=["POST"])
def addsensor():
    if request.is_json:
        req_data = request.get_json()

        try:
            emailData = req_data["email"]
            sensorNameData = req_data["sensorName"]
            hostnameData = req_data["hostname"]
            ipData = req_data["ipAddress"]
            interfaceData = req_data["netInterface"]
            locationData = req_data["location"]
            companyData = req_data["company"]
        except Exception as err:
            print("[Error] : {}".format(err))
            return nice_json(raise_json_code(400, "Variable Error, Please Fill All the Field"))

        try:
            sensor = Sensor(
                hostname=hostnameData,
                ip_address=ipData,
                net_interfaces=interfaceData,
                location=locationData,
                company=companyData,
                topic=Topic()
            )
            sensor.set_sensor_name(sensorNameData)
            user = User.objects.get({'_id' : emailData})
            user.add_sensor(sensor)
            user.save()
        except ValidationError as ve:
            print("[Error] : {}".format(ve.message))
            return nice_json(raise_json_code(400, "Paramter Not Valid"))
        except DuplicateKeyError:
            print("[Error] : Duplicate email")
            return nice_json(raise_json_code(400, "There is already user with that email address."))

        return nice_json(raise_json_code_with_data(200, "Add Sensor Success", sensor.to_son().to_dict()))
    
    else:
        return nice_json(raise_json_code(400, "Please send proper request in json"))

@app.route("/api/v1/users/<email>/sensors", methods=["GET"])
def get_user_sensor(email):
    try:
        oneUser = User.objects.get({'_id' : email})
    except User.DoesNotExist:
        return nice_json(raise_json_code(400, "User Not Found"))

    return nice_json(raise_json_code_with_data(200, "OK", oneUser.to_son().to_dict()))

@app.route("/api/v1/users/<email>/<sensorname>", methods=["GET"])
def get_individual_sensor(email, sensorname):
    try:
        oneUser = User.objects.get({'_id' : email})
    except User.DoesNotExist:
        return nice_json(raise_json_code(400, "User Not Found"))

    sensorJson = None
    for sensor in oneUser.sensor:
        if sensor.sensor_name_data == sensorname:
            sensorJson = sensor.to_son().to_dict()
    
    if sensorJson is not None:
        return nice_json(raise_json_code_with_data(200, "OK", sensorJson))
    else:
        return nice_json(raise_json_code(400, "Sensor Didn't Exist"))