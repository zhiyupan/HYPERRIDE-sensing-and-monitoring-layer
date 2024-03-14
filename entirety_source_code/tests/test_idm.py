import string

import pytest
import random
from keycloak import KeycloakAdmin

from datamodel import Datamodel
from fiware import Orion
from forms import FormService
from idm import IDM


@pytest.fixture(scope='session')
def docker_keycloack(docker_services):
    docker_services.start('keycloak')
    public_port = docker_services.wait_for_service("keycloak", 8080)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


@pytest.fixture(autouse=True)
def init():
    keycloack = KeycloakAdmin(server_url='http://localhost:8080/auth/',
                              username='admin',
                              password='Pa55w0rd',
                              realm_name='master',
                              verify=True)
    keycloack.realm_name = 'n5geh_devices'
    keycloack.create_user({"username": 'device_wizard',
                           "credentials": [{"value": "password", "type": "password", }],
                           "enabled": True,
                           "firstName": 'Device',
                           "lastName": 'Wizard'})
    user_id = keycloack.get_user_id("device_wizard")
    client_id = keycloack.get_client_id("realm-management")
    role = keycloack.get_client_role(client_id=client_id, role_name="manage-users")
    keycloack.assign_client_role(client_id=client_id, user_id=user_id, roles=[role])


@pytest.fixture
def orion():
    config = {
        'orion': 'http://localhost:1026'
    }
    return Orion(config)


@pytest.fixture
def idm():
    config = {
        "server": "http://localhost:8080/auth/",
        "username": "device_wizard",
        "password": "password",
        "realm_name": "n5geh_devices"
    }
    return IDM(config)


@pytest.fixture
def datamodel():
    config = {
        "ngsi2": "datamodel/NGSI2",
        "ngsi-ld": "datamodel/NGSI-LD",
        "classes": "datamodel/classes"
    }
    return Datamodel(config)


def test_create_entity(idm, datamodel, orion, docker_keycloack):
    formservice = FormService()
    for file in datamodel.device_types:
        device_type = formservice.get_device_type(file)
        device_id = 'urn:ngsi-ld:{}:{}'.format(device_type, ''.join(
            [random.choice(string.ascii_letters + string.digits) for n in range(32)]))
        idm.create_entity(device_id, device_type)
        idm.delete_entity(device_id)
