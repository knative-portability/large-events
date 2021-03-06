# users microservice - Large Events (Knative Proof of Portability)

Authenticate with Google Sign-In, edit and fetch authorization level of users.

These instructions are specific to this microservice. For general instructions and other information, see [the master README.md](../README.md).

### Installing

How to install and run this microservice for local development.

Each microservice has slightly different dependencies and thus slightly different installation procedures. These instructions are specific to the users microservice, but each other subfolder's README.md has an "Installing" section with more accurate instructions.

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

Set up [Google Sign-In for Websites](https://developers.google.com/identity/sign-in/web/sign-in) by creating a client ID. The users microservice needs to know the Google OAuth client ID you created. Make sure you use the same sign-in client for the users and pageserve microservices.

```sh
export GAUTH_CLIENT_ID="123-my-google-oauth-service-client-id-456"
```

After you have deployed both the users service and the pageserve service, you will need to mark users as organizers in the database for them to be authorized to create events. To do this, after a given user signs in from pageserve such that the users service inserts them into the database, find the user in the `users_collection` through your MongoDB explorer and set their `is_organizer` field to `true`.

### Running, Testing, and Deploying

The procedures for running, testing, and deploying a microservice are the same for all of the microservices. See [the master README.md](../README.md).
