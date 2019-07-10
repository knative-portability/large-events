# large-events/posts

Posts service as part of large-events project for Knative proof of portability.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
python 3+
```

### Installing

How to install and run this service for local development

Make sure your working directory is this folder

```
cd posts
```

Set up and activate a virtual environment

```
python3 -m venv venv && . venv/bin/activate
```

Install required python modules

```
pip3 install requirements.txt
```

### Running the service

Use flask to run the service locally

```
FLASK_APP=app.py && flask run
```

## Running the tests

```
python3 -m unittest -v test.py
```

## Deployment

This project is set up for continuous deployment to Google Cloud Run (managed) via [Cloud Build](https://cloud.google.com/run/docs/continuous-deployment), and it will automatically be built and deployed on pushes to the master branch of [this repo](https://github.com/knative-portability/large-events).

You can also manually deploy this service to Cloud Run. For example:

```
gcloud builds submit --tag gcr.io/knative-portability-2019/posts && \
gcloud beta run deploy --image gcr.io/knative-portability-2019/posts --platform managed
```

## Built With

* [Flask](http://flask.pocoo.org/) - Python web service framework
* [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Cloud NoSQL database

## Contributing

<!--
TODO(mukobi) add contributing to the main repo and link to it
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.
-->

## Authors

* **Gabriel Mukobi** - *Initial work* - [mukobi](https://github.com/mukobi)

See also the list of [contributors](https://github.com/knative-portability/large-events/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](../LICENSE.md) file for details.
