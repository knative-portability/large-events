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

### Running the service

To locally run this microservice, execute `app.py` with Python.

```sh
python3 app.py
```

## Running the tests

Testing again is handled on the microservice level. To test, ensure your working directory is this microservice's subfolder then use `unittest`.

```sh
python3 -m unittest discover
```

To see code coverage, use Coverage.py

```sh
# install coverage if you don't already have it
python3 -m pip install --upgrade coverage
# run coverage on all discovered tests analyzing the 'app' package
coverage run -m --source app unittest discover
# report coverage with line numbers
coverage report -m
```

## Deployment

This project is built for Knative and should be able to be deployed on any cloud product built on Knative or on any Kubernetes cluster. It has been tested on [Google Cloud Run](https://cloud.google.com/run/).

This project is set up for continuous deployment to Google Cloud Run (managed) via [Cloud Build](https://cloud.google.com/run/docs/continuous-deployment), and it will automatically be built and deployed on pushes to the master branch of [this repository](https://github.com/knative-portability/large-events).

You can also [manually deploy this project to a service like Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy). For example, to deploy this microservice to the service `events` in the GCP project with ID [PROJECT-ID] run:

```sh
gcloud builds submit --tag gcr.io/[PROJECT-ID]/events
gcloud beta run deploy --image gcr.io/[PROJECT-ID]/events --platform managed
```
