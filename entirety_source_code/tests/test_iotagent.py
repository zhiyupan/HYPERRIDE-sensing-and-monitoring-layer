import datetime
import string

import pytest
import random
from wtforms import DateTimeField, StringField, SelectField

from datamodel import Datamodel
from fiware import Orion, IoTAgent
from forms import FormService

pytest_plugins = ["docker_compose"]


@pytest.fixture(scope='session')
def docker_orion(docker_services):
    docker_services.start('orion')
    public_port = docker_services.wait_for_service("orion", 1026)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


@pytest.fixture(scope='session')
def docker_iotagent(docker_services):
    docker_services.start('iot-agent')
    public_port = docker_services.wait_for_service("iot-agent", 4041)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


@pytest.fixture
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
def datamodel():
    config = {
        "ngsi2": "datamodel/NGSI2",
        "ngsi-ld": "datamodel/NGSI-LD",
        "classes": "datamodel/classes"
    }
    return Datamodel(config)


@pytest.fixture(autouse=True)
def init(orion, datamodel):
    for file in datamodel.get_classes_files():
        data = open(file, 'rt').read()
        orion.create_entity(data)


def test_iotagent_create_all_entity(iotagent, datamodel, orion, docker_orion, docker_iotagent):
    formservice = FormService()
    for file in datamodel.iotdevice_types:
        entity_form = formservice.create_form_json(file, orion, datamodel)

        entity_form = entity_form()
        props = {}
        for field in entity_form:
            if isinstance(field, DateTimeField):
                field.data = datetime.datetime.now().isoformat() + 'Z'
            # if isinstance(field, SelectField):
            #     field.data = field.choices[1]
            if isinstance(field, StringField):
                field.data = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            data = field.data
            if isinstance(data, tuple):
                data = data[0]
            props[field.name] = str(data)
        device = formservice.create_iotdevice(file, props, datamodel)
        status = iotagent.create_device(device)
        assert status['status']
        device_id = device['device_id']
        iotagent.get_entity_by_id(device_id)
        r = iotagent.delete_entity(device_id)
        assert r.status_code == 204

def test_get_version(iotagent, docker_orion):
    version = iotagent.get_version()
    assert len(version) > 0
