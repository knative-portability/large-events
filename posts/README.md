# posts microservice - Large Events (Knative Proof of Portability)

Add, edit, and fetch posts list.

These instructions are specific to this microservice. For general instructions and other information, see [the master README.md](../README.md).

### Installing

How to install and run this microservice for local development.

Each microservice has slightly different dependencies and thus slightly different installation procedures. These instructions are specific to the posts microservice, but each other subfolder's README.md has an "Installing" section with more accurate instructions.

Install into a virtualenv:

```sh
cd events
python3 -m venv venv && . venv/bin/activate
pip3 install -r requirements.txt
```

Provision a MongoDB instance (e.g. via [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)), then provide the app with its endpoint via an environment variable.

```sh
export MONGODB_URI="mongodb+srv://[username]:[password]@[cluster-address]"
```

Specific to the posts microservice, you need to [set up a Google Cloud Storage bucket](https://cloud.google.com/storage/docs/quickstart-console) and connect it to your posts microservice deployment, then provide the app with its bucket name via an environment variable.
```sh
export GCLOUD_STORAGE_BUCKET_NAME="the-name-of-your-storage-bucket"
```

Also, in order to access the bucket you need to [create a Google Cloud Service Account](https://cloud.google.com/docs/authentication/getting-started), download the application credentials json file, move the credentials file into the posts directory, and set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to point to it.
```sh
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google_application_credentials.json"
```

### Running, Testing, and Deploying

The procedures for running, testing, and deploying a microservice are the same for all of the microservices. See [the master README.md](../README.md).
