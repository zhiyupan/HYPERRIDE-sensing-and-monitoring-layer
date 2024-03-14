import json
import logging

import os
from flask import Flask, render_template, redirect, request, g
from flask_oidc import OpenIDConnect
from functools import wraps

from datamodel import Datamodel
from fiware import Orion, IoTAgent, QuantumLeap
from forms import TypesForm, FormService
from idm import IDM

logging.basicConfig(level=logging.DEBUG)


def create_app(entirety_config, client_secret):
    """Main function to create Flask app"""
    app = Flask(__name__, static_folder='../static', template_folder='../templates')

    app.config.update({
        'SECRET_KEY': 'SomethingNotEntirelySecret',
        'TESTING': True,
        'DEBUG': True,
        'OIDC_CLIENT_SECRETS': client_secret,
        'OIDC_ID_TOKEN_COOKIE_SECURE': False,
        'OIDC_REQUIRE_VERIFIED_EMAIL': False,
        'OIDC_USER_INFO_ENABLED': True,
        'OIDC_OPENID_REALM': 'n5geh',
        'OIDC_SCOPES': ['openid', 'email', 'profile'],
        'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
        'FIWARE': entirety_config['fiware'],
        'DEVICE_IDM': entirety_config['device_idm'],
        'DATAMODEL': entirety_config['datamodel'],
        'IDM': entirety_config['idm']
    })

    oidc = OpenIDConnect(app)  # OpenIDConnect provides security mechanism for API

    datamodel = Datamodel(config=app.config['DATAMODEL'])

    orion = Orion(config=app.config['FIWARE'])

    iotagent = IoTAgent(config=app.config['FIWARE'])

    quantumleap = QuantumLeap(config=app.config['FIWARE'])

    idm = IDM(config=app.config['DEVICE_IDM'])

    formservice = FormService()

    # General routes
    @app.errorhandler(404)
    def not_found(e):
        """Render not found page"""
        return render_template("404.html")

    @app.before_request
    def before_request():
        """Add user details to each request"""
        if oidc.user_loggedin:
            info = oidc.user_getinfo(['preferred_username', 'email', 'sub', 'given_name', 'family_name'])
            g.user = info.get('preferred_username')
            g.fullname = '{} {}'.format(info.get('given_name'), info.get('family_name'))
            g.account_url = app.config['IDM']['account_url']
        else:
            g.user = None
            g.fullname = None

    @app.route('/')
    def index():
        """Default web page"""
        return redirect('/dashboard')

    @app.route('/dashboard')
    @oidc.require_login
    def dashboard():
        """Dashboard web page"""
        data = {}
        data['orion_version'] = orion.get_version()
        data['iot_agent_version'] = iotagent.get_version()
        data['idm_is_active'] = idm.is_active()
        data['quantumleap_version'] = quantumleap.get_version()
        data['classes'] = datamodel.get_classes()
        data['subscription_number'] = len(orion.get_subscriptions())

        count = 0
        if data['orion_version'] != '':
            for c in data['classes']:
                count += len(orion.get_entities(c))
        data['registered_classes'] = count
        data['all_classes'] = len(datamodel.classes_file_list)
        return render_template('dashboard.html', d=data)

    @app.route('/about')
    @oidc.require_login
    def about():
        """Render About page"""
        page_name = 'About'
        page_content = 'Device Wizard is a service for registering device within N5GEH cloud platform.'
        return render_template('simple.html', page_name=page_name, page_content=page_content)

    @app.route('/help')
    @oidc.require_login
    def help():
        """Render Help page"""
        page_name = 'Help'
        page_content = 'This is a help page to explain how user can register a device in a N5GEH platform.'
        return render_template('simple.html', page_name=page_name, page_content=page_content)

    @app.route('/logout')
    def logout():
        """Performs logout by removing the session cookie."""
        oidc.logout()
        return redirect(app.config['IDM']['logout_link'])

    # Orion routes
    def select_type(device_types, fiware_service, render_page='select_type.html'):
        """Render Select type of device page for Orion and IoT Agent"""
        choices = []
        for t in device_types:
            tt = t.split('.')
            choices.append((t, tt[0],))
        form = TypesForm()
        form.types.choices = choices
        return render_template(render_page, form=form, fiware_service=fiware_service)

    def wrong_device_type(device_type, url, service):
        """Render error page with wrong device type"""
        page_name = 'Wrong device type'
        page_content = 'Could not found template for this <span class="text-warning">{}services</span> device type. Please select one from <a href="{}">+ {} page</a>.'.format(
            device_type, url, service)
        return render_template('simple.html', page_name=page_name, page_content=page_content)

    def check_orion(func):
        """Check if Orion is available"""
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if orion.get_version() == '':
                page_name, page_content = ('Orion LD', 'Could not connect to the Orion LD. URL: {}'.format(orion.url),)
                return render_template('simple.html', page_name=page_name, page_content=page_content)
            return func(*args, **kwargs)
        return decorated_function

    def check_keycloak(func):
        """Check if Keycloak is available"""
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not idm.is_active():
                page_name, page_content = ('Keycloack', 'Could not connect to the Keycloack IDM. URL: {}'.format(idm.config['server']),)
                return render_template('simple.html', page_name=page_name, page_content=page_content)
            return func(*args, **kwargs)
        return decorated_function

    def check_iotagent(func):
        """Check if IoT Agent is available"""
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if iotagent.get_version() == '':
                page_name, page_content = ('IoT Agent', 'Could not connect to the IoT Agent. URL: {}'.format(iotagent.url),)
                return render_template('simple.html', page_name=page_name, page_content=page_content)
            return func(*args, **kwargs)
        return decorated_function

    def check_quantumleap(func):
        """Check if QuantumLeap is available"""
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if quantumleap.get_version() == '':
                page_name, page_content = ('QuantumLeap', 'Could not connect to the QuantumLeap. URL: {}'.format(quantumleap.url),)
                return render_template('simple.html', page_name=page_name, page_content=page_content)
            return func(*args, **kwargs)
        return decorated_function

    @app.route('/orion/device', methods=['GET', 'POST'])
    @oidc.require_login
    @check_orion
    @check_keycloak
    def orion_device():
        """Render Device Wizard page"""
        device_type = request.args.get('types')
        if device_type is None:
            return select_type(datamodel.device_types, 'Orion LD')

        if device_type not in datamodel.device_types:
            return wrong_device_type(device_type, '/orion/device', 'Orion LD')

        form, properties_dict = formservice.create_form_template(device_type, orion, datamodel)

        if request.method == 'POST':
            form = form(request.form)
            if form.validate():
                params = {}
                for fieldname, value in form.data.items():
                    if fieldname.endswith('_datetime'):
                        params[fieldname] = value.isoformat() + 'Z'
                    else:
                        params[fieldname] = value

                entity = datamodel.create_entity(device_type, params)
                result = orion.create_entity(entity)

                id_key = properties_dict['id'][2]
                device_type = formservice.get_device_type(device_type)
                idm.create_entity('urn:ngsi-ld:{}:{}'.format(device_type, params[id_key]), device_type)

                if result['status']:
                    page_name = 'Success'
                    page_content = 'Entity successfully created. Go to <a href="/orion/devices">Orion LD devices page</a>.'
                    return render_template('simple.html', page_name=page_name, page_content=page_content)
                else:
                    page_name = 'Failed'
                    page_content = 'Could not create entity. <a href="" onclick="windows.back()">Go Back</a> <br/>Reason: <span class="text-danger">{}</span>'.format(
                        result['error'])
                    return render_template('simple.html', page_name=page_name, page_content=page_content)

        return render_template('form_generator.html', form=form(), action='Register', fiware_service='Orion LD')

    @app.route('/orion/edit_device', methods=['GET', 'POST'])
    @oidc.require_login
    @check_orion
    def orion_edit_device():
        """Edit device properties"""
        device_id = request.args.get('id')
        device_type = request.args.get('type')

        form = formservice.create_form_entity(device_id, device_type, orion, datamodel)

        if request.method == 'POST':
            filled_form = form(request.form)
            if filled_form.validate():
                result = orion.update_entity(device_id, formservice.create_entity_update(filled_form.data.items()))
                if result['status']:
                    page_name = 'Success'
                    page_content = 'Entity successfully updated. Go to <a href="/orion/device">+ Orion LD page</a>.'
                    return render_template('simple.html', page_name=page_name, page_content=page_content)
                else:
                    page_name = 'Failed'
                    page_content = 'Could not update entity. <a href="" onclick="windows.back()">Go Back</a> <br/>Reason: <span class="text-danger">{}</span>'.format(
                        result['error'])
                    return render_template('simple.html', page_name=page_name, page_content=page_content)

        return render_template('form_generator.html', form=form(), action='Update', fiware_service='Orion LD')

    @app.route('/orion/devices', methods=['GET', 'POST'])
    @oidc.require_login
    @check_orion
    @check_keycloak
    def get_orion_devices():
        """Render list of Orion devices page"""
        device_type = request.args.get('types')
        if device_type is None:
            return select_type(datamodel.device_types, 'Orion LD', render_page='orion/devices.html')

        if device_type not in datamodel.device_types:
            return wrong_device_type(device_type, '/orion/device', 'Orion LD')

        device_type = device_type.split(".")[0]
        devices = orion.get_entities(device_type)
        for device in devices:
            device['mqtt_topic'] = idm.create_topic(device['id'], device_type)
            device['mqtt_user'] = device['id'].lower()
        return render_template('orion/devices_to_json.html', devices=devices, device_type=device_type)

    @app.route('/orion/subscriptions', methods=['GET', 'POST'])
    @oidc.require_login
    @check_orion
    def get_orion_subscriptions():
        """Render Orion subscrpitions page"""
        return render_template('orion/subscriptions.html')

    @app.route('/orion/subscriptions_to_json', methods=['GET', 'POST'])
    @oidc.require_login
    def get_orion_subscriptions_json():
        """Render Orion subscriptions as JSON"""
        subscriptions = orion.get_subscriptions()
        return render_template('orion/subscriptions_to_json.html', subscriptions=subscriptions)

    @app.route('/orion/delete', methods=['GET'])
    @oidc.require_login
    @check_orion
    @check_keycloak
    def orion_delete():
        """Delete device from Orion"""
        device_id = request.args.get('device_id')
        orion.delete_entity(device_id)
        idm.delete_entity(device_id)
        return "true"

    @app.route('/orion/init_subscriptions', methods=['GET'])
    @oidc.require_login
    @check_orion
    @check_quantumleap
    def orion_init_subscription():
        """Init QuantumLeap subscriptions in Orion for the Datamodel"""
        devices_types = datamodel.iotdevice_types
        for devices_type in devices_types:
            try:
                result = orion.create_subscription(devices_type)
            except Exception as e:
                pass
        page_name = 'Success'
        page_content = 'Subscriptions successfully registered. Go to <a href="/iotagent/device">+ IoT Agent device</a>.'
        return render_template('simple.html', page_name=page_name, page_content=page_content)

    @app.route('/orion/delete_subscription', methods=['GET'])
    @oidc.require_login
    @check_orion
    def orion_delete_subscription():
        """Delete subscription from Orion"""
        subcription_id = request.args.get('subscription_id')
        r = orion.delete_subscription(subcription_id)
        return "true"

    @app.route('/orion/register_classes', methods=['GET'])
    @oidc.require_login
    @check_orion
    def orion_register_classes():
        """Register properties classes for the Datamodel"""
        classes = datamodel.get_classes_files()
        for cls in classes:
            if os.path.isfile(cls):
                data = open(cls, 'rt').read()
                try:
                    result = orion.create_entity(data)
                except Exception as e:
                    pass
        page_name = 'Success'
        page_content = 'Classes successfully registered. Go to <a href="/iotagent/device">+ IoT Agent device</a>.'
        return render_template('simple.html', page_name=page_name, page_content=page_content)

    # IoT Agent routes
    @app.route('/iotagent/device', methods=['GET', 'POST'])
    @oidc.require_login
    @check_orion
    @check_keycloak
    @check_iotagent
    def iotagent_device():
        """Render page for IoT Agent device"""
        device_type = request.args.get('types')
        if device_type is None:
            return select_type(datamodel.iotdevice_types, 'IoT Agent')

        if device_type not in datamodel.iotdevice_types:
            return wrong_device_type(device_type, '/iotagent/device', 'IoT Agent')

        form = formservice.create_form_json(device_type, orion, datamodel)

        if request.method == 'POST':
            form = form(request.form)
            if form.validate():
                params = {}
                for fieldname, value in form.data.items():
                    if fieldname.endswith('_datetime'):
                        params[fieldname] = value.isoformat() + 'Z'
                    else:
                        params[fieldname] = value

                services = iotagent.get_services()
                apikey = IDM.create_apikey(device_type)
                is_service_exist = False
                for service in services['services']:
                    if service['apikey'] == apikey:
                        is_service_exist = True
                if not is_service_exist:
                    iotagent.create_service(apikey, device_type)

                device = formservice.create_iotdevice(device_type, params, datamodel)

                result = iotagent.create_device(device)

                idm.create_entity(device['entity_name'], device['entity_type'])

                if result['status']:
                    page_name = 'Success'
                    page_content = 'Entity successfully registered. Go to <a href="/iotagent/devices">IoT Agent registered devices page</a>.'
                    return render_template('simple.html', page_name=page_name, page_content=page_content)
                else:
                    page_name = 'Failed'
                    page_content = 'Could not register entity. <a href="" onclick="windows.back()">Go Back</a> <br/>Reason: <span class="text-danger">{}</span>'.format(
                        result['error'])
                    return render_template('simple.html', page_name=page_name, page_content=page_content)

        return render_template('form_generator.html', form=form(), action='Register', fiware_service='IoT Agent')

    @app.route('/iotagent/devices', methods=['GET', 'POST'])
    @oidc.require_login
    @check_iotagent
    @check_keycloak
    def get_iotagent_devices():
        """Render IoT Agent devices"""
        return render_template('iotagent/devices.html')

    @app.route('/iotagent/devices_to_json', methods=['GET', 'POST'])
    @oidc.require_login
    def get_iotagent_devices_json():
        """Render IoT Agent devices as JSON"""
        devices = iotagent.get_entities()
        for device in devices['devices']:
            device['mqtt_topic'] = idm.create_topic(device['entity_name'], device['entity_type'])
            device['mqtt_user'] = device['entity_name'].lower()
        return render_template('iotagent/devices_to_json.html', devices=devices)

    @app.route('/iotagent/services', methods=['GET', 'POST'])
    @oidc.require_login
    @check_iotagent
    def get_iotagent_services():
        """Render IoT Agent services"""
        return render_template('iotagent/services.html')

    @app.route('/iotagent/services_to_json', methods=['GET', 'POST'])
    @oidc.require_login
    def get_iotagent_services_json():
        """Render IoT Agent services as JSON"""
        services = iotagent.get_services()
        return render_template('iotagent/services_to_json.html', services=services)

    @app.route('/iotagent/delete_service', methods=['GET'])
    @oidc.require_login
    @check_orion
    def iotagent_delete_service():
        """Delete service from IoT Agent"""
        apikey = request.args.get('apikey')
        resource = request.args.get('resource')
        iotagent.delete_service(apikey, resource)
        return "true"

    @app.route('/iotagent/delete_device', methods=['GET'])
    @oidc.require_login
    @check_iotagent
    @check_keycloak
    def iotagent_delete_device():
        """Delete device from IoT Agent"""
        device_id = request.args.get('device_id')
        iotagent.delete_entity(device_id)
        idm.delete_entity(device_id)
        return "true"

    return app


# if __name__ == '__main__':
device_wizard = os.environ.get("DEVICE_WIZARD_CONFIG", default="entirety.json")
client_secret = os.environ.get("CLIENT_SECRET", default="client_secrets.json")
device_wizard_config = json.load(open(device_wizard, 'rt'))

app = create_app(device_wizard_config, client_secret)
# app.run(host='0.0.0.0', port=8090)
