import glob
import json
from pathlib import Path

import os
from jinja2 import Environment, FileSystemLoader, meta


class Datamodel(object):
    _ngsi2 = ''
    _ngsi_ld = ''
    _classes = ''
    device_types = []
    iotdevice_types = []

    def __init__(self, config):
        self._ngsi2 = config['ngsi2']
        self._ngsi_ld = config['ngsi-ld']
        self._classes = config['classes']

        self.device_types = self.get_dir_list(self._ngsi_ld)
        if self.device_types is not None and len(self.device_types) > 0:
            self.device_types.sort()
        self.iotdevice_types = self.get_dir_list(self._ngsi2, extension='.json')
        if self.iotdevice_types is not None and len(self.iotdevice_types) > 0:
            self.iotdevice_types.sort()
        self.classes_file_list = self.get_classes_files()
        self.classes_list = self.get_classes()

    def get_variables(self, filename):
        variables = []
        env = Environment(loader=FileSystemLoader(searchpath=self._ngsi_ld))

        template_source = env.loader.get_source(env, filename)[0]
        parsed_content = env.parse(template_source)
        templates = list(meta.find_referenced_templates(parsed_content))
        if len(templates) > 0:
            for template in templates:
                for variable in self.get_variables(template):
                    variables.append(variable)
        for variable in meta.find_undeclared_variables(parsed_content):
            variables.append(variable)
        return variables

    def create_entity(self, device_type, properties):
        env = Environment(loader=FileSystemLoader(searchpath=self._ngsi_ld))
        template = env.get_template(device_type)
        return template.render(properties)

    def get_properties_dict(self, device_type):
        variables = self.get_variables(device_type)

        # Get all properties from Data Model template itself
        properties_dict = {}
        for property in variables:
            splitted_property = property.split('_')
            key = splitted_property[0]
            order = splitted_property[1]
            name = splitted_property[2]
            data_type = splitted_property[3]
            optional = splitted_property[4]
            properties_dict[key] = (order, name, property, optional, data_type, None,)

        return properties_dict

    def create_iotdevice_from_json(self, device_type):
        device = {}

        with open('{}/{}'.format(self._ngsi2, device_type), 'rt') as f:
            device_by_type = json.load(f)
            for key, value in device_by_type.items():
                device[key] = value

        if 'base_template' in device:
            with open('{}/{}'.format(self._ngsi2, device['base_template']), 'rt') as f:
                device_base = json.load(f)
                for key, value in device_base.items():
                    if key in device and type(value) == list:
                        device[key] += value
                    else:
                        device[key] = value

        device.pop('base_template', None)

        return device

    def get_dir_list(self, datamodel_path, extension='.template'):
        return [f for f in os.listdir(datamodel_path) if os.path.isfile(os.path.join(datamodel_path, f)) and Path(
            os.path.join(datamodel_path, f)).suffix == extension]

    def get_classes_files(self):
        return glob.glob('{}/*/*.jsonld'.format(self._classes))

    def get_classes(self):
        return [f for f in os.listdir(self._classes) if os.path.isdir(os.path.join(self._classes, f))]
