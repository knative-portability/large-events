# Large Events

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
    * You will need to supply environmental variable to the microservices specifying each others' endpoints
* Each subfolder has its own README.md with more specific information regarding building, testing, deployment, etc.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system. Because of this microservice architecture, each subfolder will need to be deployed as its own independent subfolder. For specific instructions, see the README.md file in each subfolder, but generally, they all follow the following pattern:

### Prerequisites

These microservices are written in [Python 3](https://www.python.org/) and should run on Python 3.6+.

### Installing

How to install and run each microservice for local development.

Make sure your working directory is the microservice's subfolder. For example, for the "users" microservice:

```
cd users
```

Set up and activate a virtual environment.

```
python3 -m venv venv && . venv/bin/activate
```

Install the required python modules.

```
pip3 install -r requirements.txt
```

Provision a MongoDB instance (e.g. via [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)), then provide the app with its endpoint via an environmental variable.

```
export MONGODB_URI="mongodb+srv://[username]:[password]@[cluster-address]"
```

### Running the service

Use flask to run the microservice locally.

```
FLASK_APP=app.py && flask run
```

## Running the tests

Testing again is handled on the microservice level. To test, ensure your working directory is the microservice's subfolder then use `unittest`.

```
python3 -m unittest test.py
```

## Deployment

This project is built for Knative and should be able to be deployed on any cloud product built on Knative. It has been tested on [Google Cloud Run](https://cloud.google.com/run/).

This project is set up for continuous deployment to Google Cloud Run (managed) via [Cloud Build](https://cloud.google.com/run/docs/continuous-deployment), and it will automatically be built and deployed on pushes to the master branch of [this repository](https://github.com/knative-portability/large-events).

You can also [manually deploy this project to a service like Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy). For example, to deploy one of the microservices to the service [SERVICE] in the GCP project with ID [PROJECT-ID] run:

```
gcloud builds submit --tag gcr.io/[PROJECT-ID]/[SERVICE]
gcloud beta run deploy --image gcr.io/[PROJECT-ID]/[SERVICE] --platform managed
```

## Built With

* [Flask](http://flask.pocoo.org/) - Python web service framework
* [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Cloud NoSQL database

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Gabriel Mukobi** - *Initial work* - [mukobi](https://github.com/mukobi)
* **Carolyn Mei** - *Initial work* - [cmei4444](https://github.com/cmei4444)

See also the list of [contributors](https://github.com/knative-portability/large-events/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details.
