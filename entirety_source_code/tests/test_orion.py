import datetime
import string

import pytest
import random
from wtforms import DateTimeField, StringField, SelectField

from datamodel import Datamodel
from fiware import Orion
from forms import FormService

pytest_plugins = ["docker_compose"]


@pytest.fixture(scope='session')
def docker_orion(docker_services):
    docker_services.start('orion')
    public_port = docker_services.wait_for_service("orion", 1026)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


@pytest.fixture
def orion():
    config = {
        'orion': 'http://localhost:1026'
    }
    return Orion(config)


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


def test_orion_create_all_entity(orion, datamodel, docker_orion):
    for file in datamodel.device_types:
        formservice = FormService()
        # file = datamodel.device_types[0]

        entity_form, properties = formservice.create_form_template(file, orion, datamodel)

        entity_form = entity_form()
        props = {}
        for field in entity_form:
            if isinstance(field, DateTimeField):
                field.data = datetime.datetime.now()
            if isinstance(field, SelectField):
                field.data = field.choices[1]

            if isinstance(field, StringField):
                field.data = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

            data = field.data

            if isinstance(data, tuple):
                data = data[0]
            props[field.name] = data

        entity = datamodel.create_entity(file, props)
        status = orion.create_entity(entity)
        assert status['status']
        id = 'urn:ngsi-ld:{}:{}'.format(formservice.get_device_type(file), props['id_0_id_string_req'])
        orion.get_entity_by_id(id)
        r = orion.delete_entity(id)
        assert r.status_code == 204

def test_get_entities(orion, datamodel, docker_orion):
    classes = datamodel.get_classes()
    count = 0
    for c in classes:
        count += len(orion.get_entities(c))
    assert count == len(datamodel.classes_file_list)

def test_get_version(orion, docker_orion):
    version = orion.get_version()
    assert len(version) > 0
