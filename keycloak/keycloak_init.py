from keycloak import KeycloakAdmin
import psycopg2

keycloack = KeycloakAdmin(server_url='http://keycloak:8080/auth/',
                          username='admin',
                          password='Pa55w0rd',
                          realm_name='master',
                          verify=True)

keycloack.realm_name = 'n5geh'
# Create a new user for device wizard
user_id = keycloack.get_user_id("n5geh")
if user_id is None:
    keycloack.create_user({"username": 'n5geh',
                           "credentials": [{"value": "n5geh", "type": "password", }],
                           "enabled": True,
                           "firstName": 'n5geh',
                           "lastName": 'n5geh'})
    user_id = keycloack.get_user_id("n5geh")
    client_id = keycloack.get_client_id("realm-management")
    role = keycloack.get_client_role(client_id=client_id, role_name="manage-users")
    keycloack.assign_client_role(client_id=client_id, user_id=user_id, roles=[role])


keycloack.realm_name = 'n5geh_devices'
# Create a new user for device wizard
user_id = keycloack.get_user_id("device_wizard")
if user_id is None:
    keycloack.create_user({"username": 'device_wizard',
                           "credentials": [{"value": "password", "type": "password", }],
                           "enabled": True,
                           "firstName": 'Device',
                           "lastName": 'Wizard'})
    user_id = keycloack.get_user_id("device_wizard")
    client_id = keycloack.get_client_id("realm-management")
    role = keycloack.get_client_role(client_id=client_id, role_name="manage-users")
    keycloack.assign_client_role(client_id=client_id, user_id=user_id, roles=[role])

user_id = keycloack.get_user_id("iotagent")
if user_id is None:
    keycloack.create_user({"username": 'iotagent',
                           "credentials": [{"value": "password", "type": "password", }],
                           "enabled": True,
                           "firstName": 'IoT',
                           "lastName": 'Agent',
                           "attributes": {"mqtt_superuser": "true"}})


conn = psycopg2.connect(
    host='postgres',
    port=5432,
    dbname='keycloak',
    user='admin',
    password='password',
)
cur = conn.cursor()
cur.execute("UPDATE REALM SET ssl_required='NONE'")
conn.commit()
cur.close()
conn.close()