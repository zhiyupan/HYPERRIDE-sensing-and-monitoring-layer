import json
from datetime import datetime

from wtforms import Form, DateTimeField, StringField, validators, SelectField, HiddenField


class TypesForm(Form):
    """WTForm class for select type of device"""
    types = SelectField(u'Type', id='select_type')


class FormService(object):

    def create_form_field(self, properties_dict, orion, is_edit=False):
        properties = list(properties_dict.values())
        properties.sort()  # Sort it depends on the number in data model

        form_fields = {}

        for form_field in properties:
            (order, name, property, optional, data_type, value) = form_field
            validators_field = []
            if optional == 'req':
                validators_field = [validators.DataRequired()]

            if data_type == 'datetime':
                if value:
                    form_fields[property] = DateTimeField(name, default=value,
                                                          validators=validators_field)
                else:
                    form_fields[property] = DateTimeField(name, default=datetime.now(),
                                                          validators=validators_field)
            elif data_type == 'string':
                if value:
                    form_fields[property] = StringField(name, validators=validators_field, default=value)
                else:
                    form_fields[property] = StringField(name, validators=validators_field)
            elif data_type == 'select':
                items = orion.get_entities(name)
                values = [('', '',)]
                for item in items:
                    values.append((item['id'], item['id'],))
                if value:
                    form_fields[property] = SelectField(name, choices=values, validators=validators_field,
                                                            default=value)
                else:
                    form_fields[property] = SelectField(name, choices=values, validators=validators_field)
            else:
                items = orion.get_entities(data_type)
                values = [('', '',)]
                for item in items:
                    values.append((item['id'], item['id'],))
                if value:
                    value = str(value).replace('[', '').replace(']', '').replace('\'', '')
                    form_fields[property] = SelectField(name, validators=validators_field, default=value,
                                                        choices=values)
                else:
                    form_fields[property] = SelectField(name, validators=validators_field, choices=values)
        return form_fields

    def create_form_entity(self, device_id, device_type, orion, datamodel):
        """Create WTForm object from entity"""

        properties_dict = datamodel.get_properties_dict(device_type)

        device = orion.get_entity_by_id(device_id)
        form_fields = {}

        class DynamicForm(Form):
            """Dynamic form object for managing WTForm"""
            pass

        form_fields['device_id'] = StringField('id', default=device_id, render_kw={'readonly': True})
        form_fields['device_type'] = StringField('Type', default=self.get_device_type(device_type), render_kw={'readonly': True})
        form_fields['context'] = HiddenField('context', default=device['@context'])

        properties = {}
        for key, value in device.items():
            if 'type' in value and value['type'] == 'Property':
                if key in properties_dict:
                    (order, name, property, optional, data_type, val) = properties_dict[key]
                    properties[key] = (order, name, key, optional, data_type, value['value'],)

            if 'type' in value and value['type'] == 'Relationship':
                if key in properties_dict:
                    (order, name, property, optional, data_type, val) = properties_dict[key]
                    properties[key] = (order, name, key, optional, data_type, self.relationship_value(value['object']),)

        form_fields.update(self.create_form_field(properties, orion))

        for key, value in form_fields.items():
            setattr(DynamicForm, key, value)

        return DynamicForm

    def create_entity_update(self, params):
        values = {}
        for key, value in params:
            if key == 'context':
                values['@context'] = value
            elif key == 'device_id':
                continue
            else:
                values[key] = {'type': 'Property', 'value': value}
        return json.dumps(values)

    def relationship_value(self, value):
        if value is not None:
            return str(value).replace('[', '').replace(']', '').replace('\'', '')
        return value

    def create_form_json(self, device_type, orion, datamodel):
        """Generate forms based on the provided data template"""
        device = datamodel.create_iotdevice_from_json(device_type)

        form_fields = {}

        class DynamicForm(Form):
            """Dynamic form object for managing WTForm"""
            pass

        for key, value in device.items():
            if type(value) == dict:
                validators_field = []
                if value['required'] == 'true':
                    validators_field = [validators.DataRequired()]
                form_fields[value['name']] = StringField(value['label'], validators=validators_field)

        for attr in device['static_attributes']:
            validators_field = []
            if attr['required'] == 'true':
                validators_field = [validators.DataRequired()]

            if attr['type'] == 'Property' or 'query' not in attr or attr['query'] == '':
                form_fields[attr['name']] = StringField(attr['label'], validators=validators_field)
            else:
                items = orion.get_entities(attr['query'])
                values = [('', '',)]
                for item in items:
                    values.append((item['id'], item['id'],))
                form_fields[attr['name']] = SelectField(attr['label'], choices=values, validators=validators_field)

        for key, value in form_fields.items():
            setattr(DynamicForm, key, value)

        return DynamicForm

    def create_iotdevice(self, device_type, params, datamodel):
        device = datamodel.create_iotdevice_from_json(device_type)

        for key, value in device.items():
            if type(value) == dict:
                val = params[value['name']]
                if 'prefix' in value:
                    val = value['prefix'] + val
                device[key] = val

        device['entity_name'] = device['device_id']

        static_attributes = []
        for attr in device['static_attributes']:
            value = ''
            if attr['name'] in params:
                value = params[attr['name']]
            static_attributes.append({
                'name': attr['name'],
                'type': attr['type'],
                'value': value
            })
        device['static_attributes'] = static_attributes
        return device

    def create_form_template(self, device_type, orion, datamodel):
        """Create WTForm object from template"""
        properties_dict = datamodel.get_properties_dict(device_type)

        form_fields = self.create_form_field(properties_dict, orion)

        class DynamicForm(Form):
            """Dynamic form object for managing WTForm"""
            pass

        for key, value in form_fields.items():
            setattr(DynamicForm, key, value)

        return DynamicForm, properties_dict

    def get_device_type(self, device_type):
        """Convert file name to Device Type"""
        if device_type.find('.') > 0:
            return device_type.split('.')[0]
        return device_type
