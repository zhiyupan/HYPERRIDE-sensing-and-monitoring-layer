import datetime
import string

import pytest
import random
from bs4 import BeautifulSoup
from flask import appcontext_pushed, g
from keycloak import KeycloakAdmin

import main
from datamodel import Datamodel
from fiware import Orion, IoTAgent
from forms import FormService
from idm import IDM


@pytest.fixture
def client():
    device_wizard_config = {
        "device_idm": {
            "server": "http://localhost:8080/auth/",
            "username": "device_wizard",
            "password": "password",
            "realm_name": "n5geh_devices"
        },
        "fiware": {
            "orion": "http://localhost:1026",
            "iotagent": "http://localhost:4041",
            "quantumleap": "http://localhost:8668"
        },
        "datamodel": {
            "ngsi2": "datamodel/NGSI2",
            "ngsi-ld": "datamodel/NGSI-LD",
            "classes": "datamodel/classes"
        },
        "idm": {
            "logout_link": "http://localhost:8080/auth/realms/n5geh/protocol/openid-connect/logout?referrer=flask-app&redirect_uri=http%3A%2F%2Flocalhost%3A8090%2Fdashboard"
        }
    }
    app = main.create_app(device_wizard_config, 'client_secrets.json')
    app.testing = True
    app.config['TESTING'] = True
    app.before_request_funcs[None] = []

    def handler(sender, **kwargs):
        g.oidc_id_token = 'foobar'

    client = app.test_client()
    with appcontext_pushed.connected_to(handler, app):
        yield client

@pytest.fixture(scope='session')
def docker_orion(docker_services):
    docker_services.start('orion')
    public_port = docker_services.wait_for_service("orion", 1026)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url

@pytest.fixture(scope='session')
def docker_keycloack(docker_services):
    docker_services.start('keycloak')
    public_port = docker_services.wait_for_service("keycloak", 8080)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


@pytest.fixture(scope='session')
def docker_iotagent(docker_services):
    docker_services.start('iot-agent')
    public_port = docker_services.wait_for_service("iot-agent", 4041)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url

@pytest.fixture(scope='session')
def datamodel():
    config = {
        "ngsi2": "datamodel/NGSI2",
        "ngsi-ld": "datamodel/NGSI-LD",
        "classes": "datamodel/classes"
    }
    return Datamodel(config)


@pytest.fixture(scope='session')
def orion():
    config = {
        'orion': 'http://localhost:1026'
    }
    return Orion(config)

@pytest.fixture
def iotagent():
    config = {
        'iotagent': 'http://localhost:4041',
        'orion': 'http://localhost:1026'
    }
    return IoTAgent(config)

@pytest.fixture
def idm():
    config = {
        "server": "http://localhost:8080/auth/",
        "username": "device_wizard",
        "password": "password",
        "realm_name": "n5geh_devices"
    }
    return IDM(config)


@pytest.fixture(autouse=True, scope='session')
def init_idm(docker_keycloack):
    keycloack = KeycloakAdmin(server_url='http://localhost:8080/auth/',
                              username='admin',
                              password='Pa55w0rd',
                              realm_name='master',
                              verify=True)
    # keycloack.create_realm(payload={"realm": "n5geh_devices"}, skip_exists=False)
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




@pytest.fixture(autouse=True, scope='session')
def init_orion(orion, datamodel, docker_orion):
    for file in datamodel.get_classes_files():
        data = open(file, 'rt').read()
        orion.create_entity(data)



def test_device_types(client, datamodel, docker_orion):
    rv = client.get('/orion/device')
    bs = BeautifulSoup(rv.data, features="html.parser")
    assert len(bs.body.find('select', attrs={'id': 'select_type'})) == len(datamodel.device_types)

# def test_iotdevice_types(client, datamodel, docker_orion):
#     rv = client.get('/iotagent/device')
#     bs = BeautifulSoup(rv.data, features="html.parser")
#     assert len(bs.body.find('select', attrs={'id': 'select_type'})) == len(datamodel.iotdevice_types)
#
#
# def test_device_types_select_correct(client, datamodel, docker_orion):
#     device_type = datamodel.device_types[0]
#     rv = client.get('/orion/device?types={}'.format(device_type))
#     bs = BeautifulSoup(rv.data, features="html.parser")
#     form = bs.find('form')
#     inputs = form.find_all('input')
#     selects = form.find_all('select')
#     properties_dict = datamodel.get_properties_dict(device_type)
#     assert len(properties_dict) == len(inputs) + len(selects)
#
# # def test_iotdevice_types_select_correct(client, datamodel, docker_orion):
# #     device_type = datamodel.iotdevice_types[0]
# #     formservice = FormService()
# #     rv = client.get('/iotdevice?types={}'.format(device_type))
# #     bs = BeautifulSoup(rv.data, features="html.parser")
# #     form = bs.find('form')
# #     inputs = form.find_all('input')
# #     selects = form.find_all('select')
# #     # device = formservice.create_iotdevice(device_type, {}, datamodel)
# #     device = datamodel.create_iotdevice_from_json(device_type)
# #     # properties_dict = datamodel.get_properties_dict(device_type)
# #     assert len(device['static_attributes']) == len(inputs) + len(selects)
#
# def test_device_types_select_wrong(client, docker_orion):
#     rv = client.get('/orion/device?types=WRONG_TYPE')
#     bs = BeautifulSoup(rv.data, features="html.parser")
#     assert len(bs.body.findAll(text='WRONG_TYPE')) > 0
#
# def test_iotdevice_types_select_wrong(client, docker_orion):
#     rv = client.get('/iotagent/device?types=WRONG_TYPE')
#     bs = BeautifulSoup(rv.data, features="html.parser")
#     assert len(bs.body.findAll(text='WRONG_TYPE')) > 0
#
# def test_create_device(client, orion, datamodel, docker_orion, docker_keycloack):
#     formservice = FormService()
#     device_type = datamodel.device_types[0]
#     url = '/orion/device?types={}'.format(device_type)
#     rv = client.get(url)
#     bs = BeautifulSoup(rv.data, features="html.parser")
#     form = bs.find('form')
#
#     inputs = form.find_all('input')
#     selects = form.find_all('select')
#     # for input in inputs:
#     #     print(input)
#     # for select in selects:
#     #     print(select)
#
#     # formdata = {}
#     # input_fields = dict((field.get('name'), field.get('value')) for field in inputs)
#     # print(input_fields)
#     # select_dields = dict((field.get('name'), field.get('value')) for field in selects)
#     # print(select_dields)
#
#     form_fields = {}
#     for select in selects:
#         opts = select.findAll('option')
#         form_fields[select.get('name')] = opts[1]['value']
#
#     for i in inputs:
#         name = i.get('name')
#         if name.find('_datetime_') > 0:
#             form_fields[name] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         #     2019-12-12 23:14:44
#         else:
#             form_fields[name] = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
#
#     for k,v in form_fields.items():
#         print('{}\t\t{}'.format(k,v))
#     device_id = form_fields['id_0_id_string_req']
#
#     r = client.post(url, data=form_fields)
#
#     device_type = formservice.get_device_type(device_type)
#     device_id = 'urn:ngsi-ld:{}:{}'.format(device_type, device_id)
#     device = orion.get_entity_by_id(device_id)
#     assert device['id'] == device_id
#
# def test_create_iotdevice(client, iotagent, datamodel, docker_orion, docker_iotagent, docker_keycloack):
#     formservice = FormService()
#     device_type = datamodel.iotdevice_types[0]
#     url = '/iotagent/device?types={}'.format(device_type)
#     rv = client.get(url)
#     bs = BeautifulSoup(rv.data, features="html.parser")
#     form = bs.find('form')
#
#     inputs = form.find_all('input')
#     selects = form.find_all('select')
#     for input in inputs:
#         print(input)
#     for select in selects:
#         print(select)
#
#     # formdata = {}
#     # input_fields = dict((field.get('name'), field.get('value')) for field in inputs)
#     # print(input_fields)
#     # select_dields = dict((field.get('name'), field.get('value')) for field in selects)
#     # print(select_dields)
#
#     form_fields = {}
#     for select in selects:
#         opts = select.findAll('option')
#         form_fields[select.get('name')] = opts[1]['value']
#
#     for i in inputs:
#         name = i.get('name')
#         if name.find('_datetime_') > 0:
#             form_fields[name] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         #     2019-12-12 23:14:44
#         else:
#             form_fields[name] = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
#
#     for k,v in form_fields.items():
#         print('{}\t\t{}'.format(k,v))
#     device_id = form_fields['device_id']
#
#     r = client.post(url, data=form_fields)
#
#     device_type = formservice.get_device_type(device_type)
#     device_id = 'urn:ngsi-ld:{}:{}'.format(device_type, device_id)
#     device = iotagent.get_entity_by_id(device_id)
#     print(device)
#     assert device['device_id'] == device_id
