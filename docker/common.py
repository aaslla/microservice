import os
import base64
import json
import logging
from urllib.request import Request
from urllib.request import urlopen

logger = logging.getLogger('microservice-common')
# values provided into environment by cumulocity platform during deployment
C8Y_BASEURL = os.getenv('C8Y_BASEURL')
C8Y_BOOTSTRAP_USER = os.getenv('C8Y_BOOTSTRAP_USER')
C8Y_BOOTSTRAP_TENANT = os.getenv('C8Y_BOOTSTRAP_TENANT')
C8Y_BOOTSTRAP_PASSWORD = os.getenv('C8Y_BOOTSTRAP_PASSWORD')


# result is Base64 encoded "tenant/user:password"
def base64_credentials(tenant, user, password):
    str_credentials = tenant + "/" + user + ":" + password
    return 'Basic ' + base64.b64encode(str_credentials.encode()).decode()


# subscriber has form of dictionary with 3 keys {tenant, user, password}
def get_subscriber_for(tenant_id):
    req = Request(
        C8Y_BASEURL + '/application/currentApplication/subscriptions')
    req.add_header('Authorization', base64_credentials(
        C8Y_BOOTSTRAP_TENANT, C8Y_BOOTSTRAP_USER, C8Y_BOOTSTRAP_PASSWORD))
    logger.debug("Request service user for tenant id " + tenant_id)
    response = urlopen(req)
    subscribers = json.loads(response.read().decode())["users"]
    return [s for s in subscribers if s["tenant"] == tenant_id][0]
