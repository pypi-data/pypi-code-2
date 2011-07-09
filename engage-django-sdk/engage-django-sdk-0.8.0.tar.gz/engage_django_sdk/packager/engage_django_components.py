"""
Code for handling the ENGAGE_DJANGO_COMPONENTS setting.
"""
from errors import ValidationError

valid_component_names = [ "Celery", "Memcached", "Mysql", "Redis", ]

def validate_django_components(component_list, prev_version_component_list,
                               results):
    failed = False
    for comp in component_list:
        if comp not in valid_component_names:
            results.error("Invalid component name in ENGAGE_DJANGO_COMPONENTS: '%s'" %
                          comp)
            failed = True
    if not failed:
        results.components = component_list


def get_resource_specs(component_list, host_id, host_key):
    specs = []
    if "Celery" in component_list:
        specs.append({"id":"celery-1", "key":{"name":"celery-django-adapter", "version":"any"},
                      "inside":{"id":host_id, "key":host_key,
                                "port_mapping": {"host":"host"}}})
    else:
        specs.append({"id":"dummy-celery-1", "key":{"name":"django-dummy-celery-adapter", "version":"any"},
                      "inside":{"id":host_id, "key":host_key,
                                "port_mapping": {"host":"host"}}})
    if "Memcached" in component_list:
        specs.append({"id":"memcache-1", "key":{"name":"memcached-django-adapter", "version":"any"},
                      "inside":{"id":host_id, "key":host_key,
                                "port_mapping": {"host":"host"}}})
    else:
        specs.append({"id":"dummycache-1", "key":{"name":"django-dummy-cache-adapter", "version":"any"},
                      "inside":{"id":host_id, "key":host_key,
                                "port_mapping": {"host":"host"}}})
    if "Redis" in component_list:
        specs.append({"id":"redis-1", "key":{"name":"redis", "version":"2.2"},
                      "inside":{"id":host_id, "key":host_key,
                                "port_mapping": {"host":"host"}}})
    if "Mysql" in component_list:
        specs.append({"id":"mysql-server", "key":{"name":"mysql-macports", "version":"5.1"},
                      "inside":{"id":host_id, "key":host_key,
                                "port_mapping": {"host":"host"}}})
    return specs

def get_additional_config_props(component_list, host_id, host_key):
    props = []
    if "Memcached" in component_list:
        pass # no additional properties
    if "Mysql" in component_list:
        props.append({"resource": "mysql-server", "name": "mysql_admin_password",
                      "type":"password", "description":"MySQL admin password",
                      "default":None, "optional":None})
    return props

