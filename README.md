# Jupyterhub


This project will give us a container running jupyterhub with WrapSpawner which runs a MesosSpawner and DockerSpawner

##### Please follow the steps for `Running it like in "prod"` to make sure all dependencies will resolve and your changes will actually work

# Run it `"locally"` for faster iterations

1. Create a `.env` file with the content below

```shell
JPY_COOKIE_SECRET=<look for it in your secrets storage solution>
CONFIGPROXY_AUTH_TOKEN=<look for it in your secrets storage solution>
JUPYTERHUB_CRYPT_KEY=<look for it in your secrets storage solution>
OAUTH_CLIENT_ID=<look for it in your secrets storage solution>
OAUTH_CLIENT_SECRET=<look for it in your secrets storage solution>
POSTGRES_PASSWORD=<whatever you want since it is running locally>
DB_PASS=<whatever you want since it is running locally>
# Start of marathon in appdev config
HUB_CONNECT_URL=http://<IP of your computer on appdev VPN>:<port you setup>
MARATHON_HOST=http://master.mesos.service.dev.ivy:8080/
# End of marathon in dev config
LOG_LEVEL=DEBUG
DB_HOST=localhost:5432
DB_USER=jupyterhub
DB_NAME=jupyterhub
SERVICE_NAME=jupyterhub
PUBLIC_URL=http://jupyterhub.local.nxtlytics.dev:8000
PATH_TO_GOOGLE_SERVICE_ACCOUNT_JSON=/path/in/your/computer/to/service/account/json/file.json
# Start of remote docker spawner config
DOCKER_HOST=tcp://<IP of docker host>:2376
PATH_TO_DOCKER_CA=/path/in/your/computer/to/docker-ca.pem
PATH_TO_JUPYTERHUB_CLIENT_KEY=/path/in/your/computer/to/jupyterhub-local-key.pem
PATH_TO_JUPYTERHUB_CLIENT_CERTIFICATE=/path/in/your/computer/to/jupyterhub-local-cert.pem
HUB_IP=<IP of your computer in that spawned container can reach you at>
# End of remote docker config
```

**Note:** `DOCKER_HOST` must include `tcp://` due to [these lines of code](https://github.com/jupyterhub/dockerspawner/blob/master/dockerspawner/dockerspawner.py#L140-L141)

2. Install configurable-http-proxy and set your path to find it

```shell
$ npm install configurable-http-proxy@4.2.0
$ export PATH="${PATH}:${PWD}/node_modules/.bin"
```

3. Start the database first by running `docker-compose up -d db`
4. `cd app`
5. `pipenv run jupyterhub` or `pipenv run jupyterhub upgrade-db && pipenv run jupyterhub` if this is the first time you connect to the database
  - **Note:** Remember to have your hostname in `/etc/hosts` (Example: `127.0.0.1 jupyterhub.local.nxtlytics.dev`)

# Run it like in `"prod"`

1.  Create a `secrets.env` file at the root of the repository with the content below

**NOTE:** `POSTGRES_PASSWORD` and `DB_PASS` should have the same values, example of these can be found in 1Password in the `Infrastructure` vault

```shell
JPY_COOKIE_SECRET=<look for it in your secrets storage solution>
CONFIGPROXY_AUTH_TOKEN=<look for it in your secrets storage solution>
JUPYTERHUB_CRYPT_KEY=<look for it in your secrets storage solution>
OAUTH_CLIENT_ID=<look for it in your secrets storage solution>
OAUTH_CLIENT_SECRET=<look for it in your secrets storage solution>
POSTGRES_PASSWORD=<whatever you want since it is running locally>
DB_PASS=<whatever you want since it is running locally>
HUB_CONNECT_URL=http://<IP of your computer on VPN>:<port you setup>
GOOGLE_SERVICE_ACCOUNT_JSON=<content of /path/in/your/computer/to/service/account/json/file.json in one line>
DOCKER_CA=<Replace new lines with literal \n>
JUPYTERHUB_CLIENT_CERTIFICATE=<Replace new lines with literal \n>
JUPYTERHUB_CLIENT_KEY=<Replace new lines with literal \n>
```

**NOTE:** `cat /path/in/your/computer/to/service/account/json/file.json | jq -c | sed 's!\\n!\\\\n!g' | pbcopy` will give you the value for `GOOGLE_SERVICE_ACCOUNT_JSON`

2. Run `docker-compose up`
