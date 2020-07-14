FROM nxtlytics/base-python38:ci.master.1.xxxxx

# Add the application code to /app
ADD jupyterhub_config.py /app

# Ensure work directory is /app
WORKDIR /app

# Install the dependencies
RUN export DEBIAN_FRONTEND=noninteractive && \
    curl -sL https://deb.nodesource.com/setup_10.x -o /tmp/nodesource_setup.sh && \
    bash /tmp/nodesource_setup.sh && \
    apt install -y nodejs libcurl4-gnutls-dev libgnutls28-dev && \
    npm install -g configurable-http-proxy@4.2.0 && \
    apt -q -y clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    pipenv sync

# Run the application
CMD cd app \
  && echo "${GOOGLE_SERVICE_ACCOUNT_JSON}" > /app/service_account.json \
  && echo "${DOCKER_CA}" > /app/docker-ca.pem \
  && echo "${JUPYTERHUB_CLIENT_CERTIFICATE}" > /app/jupyterhub-local-cert.pem \
  && echo "${JUPYTERHUB_CLIENT_KEY}" > /app/jupyterhub-local-key.pem \
  && pipenv run jupyterhub || pipenv run jupyterhub upgrade-db && pipenv run jupyterhub

EXPOSE 8000
