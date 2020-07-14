# Configuration file for jupyterhub.
import os
import logging
from urllib.parse import urlparse

class MetaConfiguration(object):
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    public_url = urlparse(os.getenv('PUBLIC_URL'))
    marathon_app_id = os.getenv('MARATHON_APP_ID')
    hub_connect_url = os.getenv('HUB_CONNECT_URL')
    severs_per_user = int(os.getenv('SERVERS_PER_USERS', 5))
    log_level = os.getenv('LOG_LEVEL', 'ERROR')
    marathon_host = os.getenv('MARATHON_HOST')
    docker_ca = os.getenv('PATH_TO_DOCKER_CA', '/app/app/docker-ca.pem')
    docker_client_cert = os.getenv('PATH_TO_JUPYTERHUB_CLIENT_CERTIFICATE', '/app/app/jupyterhub-local-cert.pem')
    docker_client_key = os.getenv('PATH_TO_JUPYTERHUB_CLIENT_KEY', '/app/app/jupyterhub-local-key.pem')
    virtualenv = os.getenv('CONTAINER_VIRTUAL_ENV','/opt/conda')
    path = os.getenv('CONTAINER_PATH', '/opt/conda/bin:/opt/conda/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
    google_service_account_json = os.getenv('PATH_TO_GOOGLE_SERVICE_ACCOUNT_JSON', '/app/app/service_account.json')
    hub_ip = os.getenv('HUB_IP')
    oauth_client_id = os.getenv('OAUTH_CLIENT_ID')
    oauth_client_secret = os.getenv('OAUTH_CLIENT_SECRET')
    jpy_user = os.getenv('JUPYTERHUB_USER')

    def container_env_vars(self, additional_env_vars={}, api_url=None):
        if api_url == None:
            api_url = self.public_url.geturl()

        jupyterhub_api_url = '{}/hub/api'.format(api_url)
        jupyterhub_activity_url = '{}/hub/api/users/{}/activity'.format(api_urli, jpy_user)
        env_vars = { **{
            'VIRTUAL_ENV': self.virtualenv,
            'PATH': self.path,
            'JUPYTERHUB_API_URL': jupyterhub_api_url,
            'JUPYTERHUB_ACTIVITY_URL': jupyterhub_activity_url,
            'JPY_HUB_API_URL': jupyterhub_api_url,
            'GDRIVE_CLIENT_ID': self.oauth_client_id,
            'GDRIVE_CLIENT_SECRET': self.oauth_client_secret,
            'GDRIVE_CALLBACK_URL': 'https://{}:8000/hub/oauth_callback'.format(self.public_url.hostname),
        }, **additional_env_vars}
        return env_vars

    def marathon_env_vars(self, additional_env_vars={}, api_url=None):
        env_vars = self.container_env_vars(additional_env_vars, api_url)
        list_of_dicts = [{k: v} for k,v in env_vars.items()]
        return list_of_dicts

    def marathon_configuration(self, additional_env_vars={}, api_url=None, **kwargs):
        marathon_env_vars = self.marathon_env_vars(additional_env_vars, api_url)
        marathon_config = { **{
          'app_prefix': 'jupyterhub',
          'marathon_host': self.marathon_host,
          'app_image': 'nxtlytics/jupyterhub-singleuser:0.0.1',
          'app_cmd': 'docker-entrypoint.sh --ip 0.0.0.0',
          'mem_limit': '512M',
          'cpu_limit': 1,
          'docker_parameters': [
              {"key": "cap-add", "value": "SYS_ADMIN"},
              {"key": "device", "value": "/dev/fuse"}
          ],
          'ports': [8888],
          'network_mode': 'BRIDGE',
          'custom_env': marathon_env_vars
        }, **kwargs}
        return marathon_config

    def docker_configuration(self, additional_env_vars={}, api_url=None, extra_host_config={}, extra_create_kwargs={}, **kwargs):
        docker_env_vars = self.container_env_vars(additional_env_vars, api_url)
        host_config = { **{
          'cap_add': ['SYS_ADMIN'],
          'devices': [{
              'PathOnHost': '/dev/fuse',
              'PathInContainer': '/dev/fuse',
              'CgroupPermissions': 'rwm'
          }]
        }, **extra_host_config}
        create_kwargs = extra_create_kwargs # Additional args to pass for container create
        docker_config = { **{
          'image': 'nxtlytics/jupyterhub-singleuser:0.0.1',
          'environment': docker_env_vars,
          'pull_policy': 'always',
          'tls_config': {
            'verify': self.docker_ca,
            'client_cert': (
              self.docker_client_cert,
              self.docker_client_key
            )
          },
          'remove': True,
          'extra_host_config': host_config,
          'extra_create_kwargs': create_kwargs
        }, **kwargs}
        return docker_config

meta_config = MetaConfiguration()

## Include any kwargs to pass to the database connection. See
#  sqlalchemy.create_engine for details.
#c.JupyterHub.db_kwargs = {}

# `psycopg2` is the default DBAPI. Source: https://docs.sqlalchemy.org/en/13/core/engines.html#postgresql
## url for the database. e.g. `postgresql+psycopg2://scott:tiger@localhost/mydatabase`
db_connection = {'user': meta_config.db_user, 'password': meta_config.db_pass, 'host': meta_config.db_host, 'db': meta_config.db_name}
c.JupyterHub.db_url = 'postgresql+psycopg2://{user}:{password}@{host}/{db}'.format(**db_connection)

## The public facing URL of the whole JupyterHub application.
#
#  This is the address on which the proxy will bind. Sets protocol, ip, base_url
c.JupyterHub.bind_url = 'http://:8000'

# Configure the Hub if the Proxy or Spawners are remote or isolated
# Source: https://jupyterhub.readthedocs.io/en/stable/getting-started/networking-basics.html#configure-the-hub-if-the-proxy-or-spawners-are-remote-or-isolated
c.JupyterHub.hub_bind_url = 'http://127.0.0.1:8081'

# Cookie secret
# Source: https://jupyterhub.readthedocs.io/en/stable/getting-started/security-basics.html#cookie-secret
# export JPY_COOKIE_SECRET=$(openssl rand -hex 32)
# Important: If the cookie secret value changes for the Hub, all single-user notebook servers must also be restarted.
# Remember to set JPY_COOKIE_SECRET in marathon

# Proxy Auth token
# Source: https://jupyterhub.readthedocs.io/en/stable/getting-started/security-basics.html#proxy-authentication-token
# export CONFIGPROXY_AUTH_TOKEN=$(openssl rand -hex 32)
# Important: If you don’t set the Proxy authentication token, the Hub will generate a random key itself, which means that any time you restart the Hub you
# must also restart the Proxy.
# Remember to set CONFIGPROXY_AUTH_TOKEN in marathon

# Authentication and users
# Source: https://jupyterhub.readthedocs.io/en/stable/getting-started/authenticators-users-basics.html
# c.PAMAuthenticator.admin_groups = {'wheel'}
# Setting `JupyterHub.admin_access` to `True` allows `admin_users` to login as other users for debugging, should we enable this?
# Remove `c.Authenticator.admin_users` completely if https://github.com/jupyterhub/oauthenticator/pull/341 is merged
#c.Authenticator.admin_users = {'ricardo', 'tyler', 'brian', 'brady'}

from oauthenticator.google import GoogleOAuthenticator
c.JupyterHub.authenticator_class = GoogleOAuthenticator
c.GoogleOAuthenticator.enable_auth_state = True

import warnings

if 'JUPYTERHUB_CRYPT_KEY' not in os.environ:
    warnings.warn(
        "Need JUPYTERHUB_CRYPT_KEY env for persistent auth_state.\n"
        "    export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)"
    )
    exit(1)

c.JupyterHub.authenticator_class.extra_authorize_params = {'access_type': 'offline', 'approval_prompt': 'force'}
c.GoogleOAuthenticator.scope = ['openid', 'email', 'https://www.googleapis.com/auth/drive']
c.GoogleOAuthenticator.client_id = meta_config.oauth_client_id
c.GoogleOAuthenticator.client_secret = meta_config.oauth_client_secret
c.GoogleOAuthenticator.oauth_callback_url = 'https://{}:8000/hub/oauth_callback'.format(meta_config.public_url.hostname)
c.GoogleOAuthenticator.hosted_domain = ['example.com']
c.GoogleOAuthenticator.login_service = 'nxtlytics'
c.GoogleOAuthenticator.gsuite_administrator = {'nxtlytics': 'admin'}
c.GoogleOAuthenticator.google_service_account_keys = {'example.com': meta_config.google_service_account_json}
c.GoogleOAuthenticator.admin_google_groups = {'example.com': ['infeng']}
c.GoogleOAuthenticator.google_group_whitelist = {'example.com': ['all-engineers', 'all'] }

# Spawners and notebooks
# Source: https://jupyterhub.readthedocs.io/en/stable/getting-started/spawners-basics.html
# c.Spawner.notebook_dir = '~/notebooks'
# c.Spawner.args = ['--debug', '--profile=PHYS131']
#c.Spawner.cmd = 'jupyter-labhub'
c.Spawner.default_url = '/lab'
c.JupyterHub.allow_named_servers = True
c.JupyterHub.named_server_limit_per_user = meta_config.severs_per_user
c.JupyterHub.spawner_class = 'wrapspawner.ProfilesSpawner'
c.Spawner.http_timeout = 120
# Set the log level by value or name.
c.JupyterHub.log_level = meta_config.log_level

# Enable debug-logging of the single-user server
if meta_config.log_level == 'DEBUG':
  c.Spawner.debug = True
  logging.getLogger('marathon').setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
# ProfilesSpawner configuration
#------------------------------------------------------------------------------
# List of profiles to offer for selection. Signature is:
#   List(Tuple( Unicode, Unicode, Type(Spawner), Dict ))
# corresponding to profile display name, unique key, Spawner class,
# dictionary of spawner config options.
#
# The first three values will be exposed in the input_template as {display},
# {key}, and {type}
#

# Custom Environment variables section

if meta_config.marathon_app_id:
  marathon_api_url = meta_config.public_url.geturl()
  docker_host_config = {}
elif meta_config.hub_connect_url:
  marathon_api_url = meta_config.hub_connect_url
  docker_host_config = {
    'extra_hosts': {
      meta_config.public_url.hostname: meta_config.hub_ip
    }
  }


def my_hook(spawner, auth_state):
    gdrive_env_var = {
      'GDRIVE_ACCESS_TOKEN': auth_state['access_token'],
      'GDRIVE_REFRESH_TOKEN': auth_state['refresh_token']
    }
    # Profiles
    small = meta_config.marathon_configuration(additional_env_vars=gdrive_env_var, api_url=marathon_api_url)
    small_scipy = meta_config.marathon_configuration(additional_env_vars=gdrive_env_var, api_url=marathon_api_url, app_image='jupyter/scipy-notebook:5438a605eba8')
    us_small = meta_config.marathon_configuration(additional_env_vars=gdrive_env_var, api_url=marathon_api_url, app_image='jupyter/tensorflow-notebook:8882c505faa8')
    us_small_scipy = meta_config.marathon_configuration(additional_env_vars=gdrive_env_var, api_url=marathon_api_url, app_image='jupyter/all-spark-notebook:8882c505faa8')
    us_small_docker = meta_config.docker_configuration(additional_env_vars=gdrive_env_var, image='jupyterhub/singleuser:1.2', extra_host_config=docker_host_config)

    # Declaration of profiles
    everybody = [
      ('Small Default', 'small', 'jmarathonspawner.marathonspawner.MarathonSpawner', small),
      ('Small SciPy', 'small-scipy', 'jmarathonspawner.marathonspawner.MarathonSpawner', small_scipy),
    ]

    engineer_only = everybody + [
      ('Engineer Only Small Default', 'small', 'jmarathonspawner.marathonspawner.MarathonSpawner', us_small),
      ('Engineer Only Small SciPy', 'small-scipy', 'jmarathonspawner.marathonspawner.MarathonSpawner', us_small_scipy),
      ('Engineer Only Small docker', 'small-docker', 'dockerspawner.DockerSpawner', us_small_docker),
    ]

    if 'all-engineers' in auth_state['google_user']['google_groups']:
        print("{} is an engineer".format(auth_state['google_user']['email']))
        spawner.profiles = engineer_only
    else:
        print("{} is not an engineer".format(auth_state['google_user']['email']))
        spawner.profiles = everybody

c.Spawner.auth_state_hook = my_hook
