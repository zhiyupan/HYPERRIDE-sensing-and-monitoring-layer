import datetime
import string

import pytest
import random
from rdflib import Graph

from datamodel import Datamodel


@pytest.fixture
def datamodel():
    config = {
        "ngsi2": "datamodel/NGSI2",
        "ngsi-ld": "datamodel/NGSI-LD",
        "classes": "datamodel/classes"
    }
    return Datamodel(config)


def test_get_dir_list(datamodel):
    assert len(datamodel.device_types) > 0
    assert len(datamodel.iotdevice_types) > 0
    assert len(datamodel.get_classes_files()) > 0


def test_ngsi_ld_read_values(datamodel):
    for file in datamodel.device_types:
        variables = datamodel.get_variables(file)
        assert len(variables) > 0


def test_ngsi_ld_create_entity(datamodel):
    for file in datamodel.device_types:
        props = {}
        properties = datamodel.get_properties_dict(file)
        for key, value in properties.items():
            (order, name, property, optional, data_type, val) = value
            if data_type == 'datetime':
                props[property] = datetime.datetime.now()
            else:
                props[property] = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        entity = datamodel.create_entity(file, props)
        Graph().parse(data=entity, format='json-ld')


def test_ngsi_ld_create_classes(datamodel):
    classes = datamodel.get_classes_files()
    for file in classes:
        entity = open(file, 'rt').read()
        Graph().parse(data=entity, format='json-ld')


def test_create_iotdevice_from_json(datamodel):
    for file in datamodel.iotdevice_types:
        datamodel.create_iotdevice_from_json(file)
        # TODO: JSON validation
