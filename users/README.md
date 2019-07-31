# users microservice - Large Events (Knative Proof of Portability)

Authenticate with Google Sign-In, edit and fetch authorization level of users.

These instructions are specific to this microservice. For general instructions and other information, see [the master README.md](../README.md).

### Installing

How to install and run this microservice for local development.

Each microservice has slightly different dependencies and thus slightly different installation procedures. These instructions are specific to the users microservice, but each other subfolder's README.md has an "Installing" section with more accurate instructions.

Make sure your working directory is this microservice's subfolder.

```sh
cd users
```

Set up and activate a virtual environment.

```sh
python3 -m venv venv && . venv/bin/activate
```

Install the required python modules.

```sh
pip3 install -r requirements.txt
```

Provision a MongoDB instance (e.g. via [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)), then provide the app with its endpoint via an environment variable.

```sh
export MONGODB_URI="mongodb+srv://[username]:[password]@[cluster-address]"
```

Set any other environment variables needed by the service. For the users service, you need to set the following:

```sh
export GAUTH_CLIENT_ID="123-my-google-oauth-service-client-id-456"
```

### Running, Testing, and Deploying

The procedures for running, testing, and deploying a microservice are the same for all of the microservices. See [the master README.md](../README.md).
