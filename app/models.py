import datetime
from pymodm import MongoModel, EmbeddedMongoModel, fields, connect
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import generate_random

connect('mongodb://localhost:27017/kaspadb')

class Topic(EmbeddedMongoModel):
    global_topic = fields.CharField(default="global_{}".format(generate_random(5)))
    command_topic = fields.CharField(default="command_{}".format(generate_random(5)))
    response_topic = fields.CharField(default="response_{}".format(generate_random(5)))

    class Meta:
        final = True
    
    def __repr__(self):
        return '<Topic {}>'.format(self.global_topic)

class Sensor(EmbeddedMongoModel):
    sensor_secret_key = fields.CharField(default=generate_random(16))
    sensor_name_data = fields.CharField()
    hostname = fields.CharField()
    ip_address = fields.GenericIPAddressField()
    net_interfaces = fields.CharField()
    location = fields.CharField()
    company = fields.CharField()
    topic = fields.EmbeddedDocumentField(Topic)

    def __repr__(self):
        return '<Sensor {}>'.format(self.sensor_name_data)

    def set_sensor_name(self, sensor_name):
        self.sensor_name_data = "{}-{}".format(sensor_name, generate_random(8))

    class Meta:
        final = True

class User(MongoModel):
    email = fields.EmailField(primary_key=True, required=True)
    username = fields.CharField(required=True)
    password_hash = fields.CharField(required=True)
    token = fields.CharField(default=generate_random(8))
    created_at = fields.DateTimeField(default=datetime.datetime.now())
    admin = fields.BooleanField(default=False)
    activated = fields.BooleanField(default=True)
    sensor = fields.EmbeddedDocumentListField(Sensor, default=[])

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def status_admin(self):
        return self.admin
    
    @status_admin.setter
    def status_admin(self, status):
        self.admin = status
    
    def add_sensor(self, sensor):
        self.sensor.append(sensor)
    
    @property
    def status_active(self):
        return self.activated

    @status_active.setter
    def status_active(self, status):
        self.activated = status
    
    class Meta:
        final = True