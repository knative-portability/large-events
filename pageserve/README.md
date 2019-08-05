# pageserve microservice - Large Events (Knative Proof of Portability)

Serve web UI and act as an API gateway to other microservices.

These instructions are specific to this microservice. For general instructions and other information, see [the master README.md](../README.md).

### Installing

How to install and run this microservice for local development.

Each microservice has slightly different dependencies and thus slightly different installation procedures. These instructions are specific to the pageserve microservice, but each other subfolder's README.md has an "Installing" section with more accurate instructions.

Install into a virtualenv:

```sh
cd events
python3 -m venv venv && . venv/bin/activate
pip3 install -r requirements.txt
```

Set up [Google Sign-In for Websites](https://developers.google.com/identity/sign-in/web/sign-in) by creating a client ID. The pageserve microservice needs to know the Google OAuth client ID you created. Make sure you use the same sign-in client for the users and pageserve microservices.

```sh
export GAUTH_CLIENT_ID="123-my-google-oauth-service-client-id-456"
```

Set any environment variables needed by the microservice. The pageserve microservice needs to know the addresses of the other microservices and a key for encrypting sessions.

```sh
export USERS_ENDPOINT="https://endpoint.where-users-is-deployed.com/v1/"
export EVENTS_ENDPOINT="https://endpoint.where-events-is-deployed.com/v1/"
export POSTS_ENDPOINT="https://endpoint.where-posts-is-deployed.com/v1/"
export FLASK_SECRET_KEY="some secure and unique string for encrypting sessions"
```

### Running, Testing, and Deploying

The procedures for running, testing, and deploying a microservice are the same for all of the microservices. See [the master README.md](../README.md).
