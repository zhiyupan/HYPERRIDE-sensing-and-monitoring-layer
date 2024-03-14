import logging

import xxhash
from keycloak import KeycloakAdmin


class IDM(object):
    config = {}

    def __init__(self, config):
        try:
            self.config = config
        except Exception as e:
            logging.error('Init IDM service for Device Registration', e)

    def _get_keycloack(self):
        return KeycloakAdmin(server_url=self.config['server'],
                             username=self.config['username'],
                             password=self.config['password'],
                             realm_name=self.config['realm_name'],
                             verify=True)

    def create_entity(self, device_id, device_type):
        mqtt_write_topics = self.create_topic(device_id, device_type)
        return self._get_keycloack().create_user({"username": device_id,
                                                  "credentials": [{"value": "secret", "type": "password", }],
                                                  "enabled": True,
                                                  "firstName": device_type,
                                                  "lastName": device_type,
                                                  "attributes": {"mqtt_write_topics": mqtt_write_topics}})

    @staticmethod
    def create_topic(device_id, device_type):
        api_key = IDM.create_apikey(device_type)
        return '/{api_key}/{id}/attrs'.format(api_key=api_key, id=device_id)

    @staticmethod
    def create_apikey(device_type):
        device_type = device_type.split(".")[0]
        api_key = xxhash.xxh64(device_type).hexdigest()
        return 'n5geh{api_key}'.format(api_key=api_key)

    def delete_entity(self, device_id):
        keycloack = self._get_keycloack()
        user_id = keycloack.get_user_id(device_id.lower())
        if user_id is not None:
            keycloack.delete_user(user_id=user_id)

    def is_active(self):
        try:
            self._get_keycloack()
            return True
        except Exception as e:
            pass
        return False
