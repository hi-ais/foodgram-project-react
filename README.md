# Graduation project FOODGRAM

![workflow](https://github.com/hi-ais/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

On the Foodgramm online service, users will be able to publish recipes, subscribe to publications of other users, add their favorite recipes to the Favorites list, and before going to the store, download a summary list of products needed to prepare one or more selected dishes.

## Built With:
- Django
- Django REST Framework
- Python
- Nginx
- PostgreSQL
- Docker
- gunicorn
- Yandex.cloud
- GitHubActions

##  Project setup
1. Clone the repository

`git@github.com:hi-ais/foodgram-project-react.git`

2. Create and activate the virtual environment:

`python -m venv venv`
`source venv/Scripts/activate`
`python -m pip install`

3. Install dependencies:

`pip install -r requirements.txt`

4. Install the flake8 linter

`pip install flake8 pep8-naming flake8-broken-line flake8-return flake8-isort`

5. Check the code against PEP8 standards and run pytest:

`python -m flake8`
`pytest`

##  Server preparation

1. Log in to your remote server in the cloud.

2. Stop the nginx service:

`sudo systemctl stop nginx`

3. Install Docker:

`sudo apt install docker.io`

4. Install docker-compose:

`sudo apt-get update`

`sudo apt-get install docker-compose-plugin`

5. Copy files docker-compose.yaml and  **directory** with the default.conf file from your project to the server in home/<your_username>/docker-compose.yaml and home/<your_username>/nginx/default.conf respectively:

`scp docker-compose.yaml <USER>@<HOST>`

`scp default.conf <USER>@<HOST>:/nginx/`

6. Create a file **.env** and fill it like this:
```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<database name postgres>
DB_USER=<database user>
DB_PASSWORD=<password>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<project secret key django>
DEBUG = False
```
## Working with Workflow
You need to add environment variables to Secrets GitHub to work:
```
DOCKER_PASSWORD=<password from DockerHub>
DOCKER_USERNAME=<username>
USER=<username to connect to the server>
HOST=<severs's IP >
PASSPHRASE=<password for the server, if set>
SSH_KEY=<your SSH key (to get the command: cat ~/.ssh/id_rsa)>

```

Workflow steps:

- Checking the code for compliance with PEP8
- Building and publishing the backend image on DockerHub.
- Automatic deployment to a remote server.

##  Application Deployment

1. You need to connect to the server.

`ssh <USER>@<HOST>` 

2. Collect containers using the command

`sudo docker compose up -d --build`

2. Navigate to the running *backend* application container with the command:

`sudo docker container exec -it <CONTAINER ID> bash`

3. Inside the container, you need to perform migrations, connect statics and create a superuser:

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py collectstatic --no-input`

`python manage.py createsuperuser`

The project will be available by your IP


Admin:
name: aiskhaidarova
password:admin08
