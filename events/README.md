# events microservice - Large Events (Knative Proof of Portability)

[![Build Status](https://travis-ci.com/knative-portability/large-events.svg?branch=master)](https://travis-ci.com/knative-portability/large-events)
[![Coverage Status](https://coveralls.io/repos/github/knative-portability/large-events/badge.svg?branch=master)](https://coveralls.io/github/knative-portability/large-events?branch=master)

Add, edit, and fetch events list.

## Introduction

An app built as proof of portability for [Knative](https://knative.dev) that provides a platform for event organizers to share info during large events like concerts, parades, expos, etc. Key features of this app include:
* Allow authorized event organizers to create and edit events
* Handle uploading and serving multimedia posts made by attendees
* Organize and filter multiple sub-events
* Provide a clean front-end web UI for interaction with the service
* Authenticate with OAuth 2.0

This app is built as part of a proof of portability project for [Knative](https://knative.dev). It is meant to show the key features of Knative, to test the conformance across various cloud product implementations of Knative, and to document with functioning sample code how one might develop, build, and deploy with Knative. Key features of Knative this app demonstrates include:
* Develop microservices independently that can be individually deployed, updated, and auto-scaled
* Deploy containerized code with minimal configuration, allowing the developer to focus on features rather than infrastructure
* Run serverless, stateful containers that enable pay-for-use billing

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This microservice is written in [Python 3](https://www.python.org/) and should run on Python 3.6+.

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

## Built With

### Development

* [Python 3](https://www.python.org/) - Python programming language
* [Flask](http://flask.pocoo.org/) - Python web service framework
* [pymongo](https://api.mongodb.com/python/current/) - MongoDB Python client
* [GitHub](https://github.com) - Development platform for open source
* [Travis CI](https://travis-ci.com/) - Hosted continuous integration service
* [Gunicorn](https://gunicorn.org/) - Python WSGI HTTP Server for UNIX

### Testing

* [unittest](https://docs.python.org/3/library/unittest.html) - Python unit testing framework
* [Coverage.py](https://coverage.readthedocs.io/en/v4.5.x/) - Python code coverage measurement tool
* [Coveralls](http://coveralls.io) - Test coverage history and statistics service 

### Services

* [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Cloud NoSQL database
* [Google Cloud Build](https://cloud.google.com/cloud-build/) - Continuous build, test, deploy in the cloud
* [Google Cloud Run](https://cloud.google.com/run/) - On top of Knative, run fully managed stateless containers

## Contributing

Please read [CONTRIBUTING.md](../CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Gabriel Mukobi** - *Initial work* - [mukobi](https://github.com/mukobi)
* **Carolyn Mei** - *Initial work* - [cmei4444](https://github.com/cmei4444)

See also the list of [contributors](https://github.com/knative-portability/large-events/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](../LICENSE.md) file for details.
