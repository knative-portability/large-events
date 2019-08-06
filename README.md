# Large Events (Knative Proof of Portability)

[![Build Status](https://travis-ci.com/knative-portability/large-events.svg?branch=master)](https://travis-ci.com/knative-portability/large-events)
[![Coverage Status](https://coveralls.io/repos/github/knative-portability/large-events/badge.svg?branch=master)](https://coveralls.io/github/knative-portability/large-events?branch=master)

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

### A note on microservices
This project is organized into microservices. Although this repository contains a few top level files such as this README.md, each direct subfolder of this project is its own independent microservice. This means a few things: 
* Each microservice subfolder is meant to be built and deployed independently from each other
* The microservices interact with each other in deployment through HTTP requests
* You will need to supply environment variable to the microservices specifying each others' endpoints
* Each subfolder has its own README.md with more specific information regarding building, testing, deployment, etc.

There are 4 microservices in this project. They are:
- [__events__](events) - Add, edit, and fetch events list.
- [__pageserve__](pageserve) - Serve web UI and act as an API gateway to other microservices.
- [__posts__](posts) - Add, edit, and fetch posts list.
- [__users__](users) - Authenticate with Google Sign-In, edit and fetch authorization level of users.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system. Because of this microservice architecture, each subfolder will need to be deployed as its own independent subfolder. For specific instructions, see the README.md file in each subfolder, but generally, they all follow the following pattern:

### Prerequisites

These microservices are written in [Python 3](https://www.python.org/) and should run on Python 3.6+.

### Installing

How to install and run each microservice for local development.

Each microservice has slightly different dependencies and thus slightly different installation procedures. Generally, installation for each microservice is as follows, but each subfolder's README.md has an "Installing" section with more accurate instructions.

Install into a virtualenv:

```sh
cd events
python3 -m venv venv && . venv/bin/activate
pip3 install -r requirements.txt
```

Provision a MongoDB instance (e.g. via [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)), then provide the app with its endpoint via an environment variable (this step is not needed for the pageserve microservice).

```sh
export MONGODB_URI="mongodb+srv://[username]:[password]@[cluster-address]"
```

Set any other environment variables needed by the microservice.

```sh
export USERS_ENDPOINT="https://endpoint.where-users-is-deployed.com/v1/"
export EVENTS_ENDPOINT="https://endpoint.where-events-is-deployed.com/v1/"
export GAUTH_CLIENT_ID="123-my-google-oauth-service-client-id-456"
export FLASK_SECRET_KEY="some secure and unique byte-string"
...
```

### Running the service

To locally run a microservice, execute `app.py` with Python.

```sh
python3 app.py
```

## Running the tests

Testing again is handled on the microservice level. To test, ensure your working directory is the microservice's subfolder then use `unittest`.

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

You can also [manually deploy this project to a service like Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy). For example, to deploy one of the microservices to the service [SERVICE] in the GCP project with ID [PROJECT-ID] run:

```sh
gcloud builds submit --tag gcr.io/[PROJECT-ID]/[SERVICE]
gcloud beta run deploy --image gcr.io/[PROJECT-ID]/[SERVICE] --platform managed
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
* [Google Cloud Storage](https://cloud.google.com/storage/) - Unified object storage for developers and enterprises
* [Google Sign-In for Websites](https://developers.google.com/identity/sign-in/web/sign-in) - OAuth 2.0 authentication library
* [Google Cloud Build](https://cloud.google.com/cloud-build/) - Continuous build, test, deploy in the cloud
* [Google Cloud Run](https://cloud.google.com/run/) - On top of Knative, run fully managed stateless containers

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Gabriel Mukobi** - *Initial work* - [mukobi](https://github.com/mukobi)
* **Carolyn Mei** - *Initial work* - [cmei4444](https://github.com/cmei4444)

See also the list of [contributors](https://github.com/knative-portability/large-events/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details.
