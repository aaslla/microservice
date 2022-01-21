#!flask/bin/python

import os
import logging
from flask import Flask, jsonify, request
from common import base64_credentials, get_subscriber_for
from cert import create_certificate_for_device

app = Flask(__name__)
logger = logging.getLogger('microservice')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.debug('Logger for microservice was initialized')
# Hello world endpoint


@app.route('/')
def hello():
    return 'Hello worldo Felix!'

# Verify the status of the microservice


@app.route('/health')
def health():
    return '{ "status" : "UP" }'

# Get environment details


@app.route('/environment')
def environment():
    environment_data = {
        'platformUrl': os.getenv('C8Y_BASEURL'),
        'mqttPlatformUrl': os.getenv('C8Y_BASEURL_MQTT'),
        'tenant': os.getenv('C8Y_BOOTSTRAP_TENANT'),
        'user': os.getenv('C8Y_BOOTSTRAP_USER'),
        'password': os.getenv('C8Y_BOOTSTRAP_PASSWORD'),
        'microserviceIsolation': os.getenv('C8Y_MICROSERVICE_ISOLATION')
    }

    return jsonify(environment_data)


@app.route('/tenant_auth')
def tenant_auth():
    return tenant_user_auth()


@app.route('/service_auth')
def service_auth():
    return service_user_auth()


@app.route('/create_Cert')
def create_cert():
    return str(create_certificate_for_device("my_device", 50))


def tenant_user_auth():
    tenant = request.authorization["username"].split('/')[0]
    user = request.authorization["username"].split('/')[0]
    password = request.authorization["password"]
    return base64_credentials(tenant, user, password)


def service_user_auth():
    tenant_id = request.authorization["username"].split('/')[0]
    service_user = get_subscriber_for(tenant_id)
    return base64_credentials(service_user['tenant'], service_user['name'], service_user['password'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
