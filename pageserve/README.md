# pageserve microservice - Large Events (Knative Proof of Portability)

Serve web UI and act as an API gateway to other services.

These instructions are specific to this microservice. For general instructions and other information, see [the master README.md](../README.md).

### Installing

How to install and run this microservice for local development.

Each microservice has slightly different dependencies and thus slightly different installation procedures. These instructions are specific to the pageserve microservice, but each other subfolder's README.md has an "Installing" section with more accurate instructions.

Make sure your working directory is this microservice's subfolder.

```sh
cd pageserve
```

Set up and activate a virtual environment.

```sh
python3 -m venv venv && . venv/bin/activate
```

Install the required python modules.

```sh
pip3 install -r requirements.txt
```

Set any environment variables needed by the service. For the pageserve service, you need to set the following:

```sh
export USERS_ENDPOINT="https://endpoint.where-users-is-deployed.com/v1/"
export EVENTS_ENDPOINT="https://endpoint.where-events-is-deployed.com/v1/"
export POSTS_ENDPOINT="https://endpoint.where-posts-is-deployed.com/v1/"
export GAUTH_CLIENT_ID="123-my-google-oauth-service-client-id-456"
export FLASK_SECRET_KEY="some secure and unique byte-string"
```

### Running, Testing, and Deploying

The procedures for running, testing, and deploying a microservice are the same for all of the microservices. See [the master README.md](../README.md).
