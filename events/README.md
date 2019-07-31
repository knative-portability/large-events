# events microservice - Large Events (Knative Proof of Portability)

Add, edit, and fetch events list.

These instructions are specific to this microservice. For general instructions and other information, see [the master README.md](../README.md).

### Installing

How to install and run this microservice for local development.

Each microservice has slightly different dependencies and thus slightly different installation procedures. These instructions are specific to the events microservice, but each other subfolder's README.md has an "Installing" section with more accurate instructions.

Make sure your working directory is this microservice's subfolder.

```sh
cd events
```

Set up and activate a virtual environment.

```sh
python3 -m venv venv && . venv/bin/activate
```

Install the required python modules.

```sh
pip3 install -r requirements.txt
```

Provision a MongoDB instance (e.g. via [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)), then provide the app with its endpoint via an environmental variable.

```sh
export MONGODB_URI="mongodb+srv://[username]:[password]@[cluster-address]"
```

### Running, Testing, and Deploying

The procedures for running, testing, and deploying a microservice are the same for all of the microservices. See [the master README.md](../README.md).
