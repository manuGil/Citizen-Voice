# Installation Guide
This guide will walk you through the process of setting up the Citizen Mapping Tool on your local machine. Follow these steps to get the development environment up and running.

The tool is designed to be set up using Docker Compose, which simplifies the process of managing dependencies and environment configurations. This guide assumes you have basic knowledge of using the command line and Docker.

## Prerequisites
Before you begin, ensure you have the following software installed on your machine:

**Docker** and **Docker Compose** (version 2.22.0 or later): Docker is required to run the project in isolated containers. Docker Compose is used to manage multi-container Docker applications.

- Install [Git](https://git-scm.com/install/)
- Install [Docker](https://docs.docker.com/get-started/get-docker/)
- Install [Docker Compose](https://docs.docker.com/compose/install/) (v2.22.0 or later)


## Getting Started
Follow these steps to set up the Citizen-Voice project:

### Step 1. Clone the Repository

Open a terminal and navigate to the directory where you want to save the project and clone the project repository using the following command:
 ```bash
git clone https://github.com/Citizens-Collective/Citizen-Voice.git
 ```

### Step 2: Checkout the Root Directory

Navigate into the project directory 
```bash
cd Citizen-Voice
``` 

### Step 3: Configure Environment Variables
Create a .env file in the project root directory with `nano .env` and paste the following configuration into the .env file and save it:

```bash
POSTGRES_USER=citizen
POSTGRES_DBASE=civo
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_DB_ENGINE=postgis
DJANGO_ALLOWED_HOSTS= localhost 127.0.0.1 [::1] api cvportal
DJANGO_DEBUG=1 # 0 for production
```

### Step 4: Set Up Secrets
Create a secrets folder in the root directory:

```shell
mkdir secrets
```
Create a `django_token.txt` file inside the secrets folder:

```shell
nano secrets/django_token.txt
```

Create a token for the Django App into this file. A token servers as very strong password, and for this case it should be a long set of alphanumeric characters with no spaces. As an example we we will use `0f0646a6985458ada71a` in the code examples.

Create a `postgres_password.txt` file inside the secrets folder:

```shell
nano secrets/postgres_password.txt
```
Paste your PostgreSQL superuser password into this file. For example: `mysecretpassword`.

(step-5-build-and-run-the-project)=
### Step 5: Build and Run the Project
Build and run the project using Docker Compose:

```bash
docker compose --env-file .env up --build
```
This command will build the Docker images and start the containers. The web server will be accessible at `http://localhost/`.
### Verify the Installation
Open a web browser and navigate to `http://localhost/` to see the development version of the survey app.

This guide should help you set up the Citizen-Voice project efficiently. If you encounter any issues, please refer to the project's documentation or seek help from the community.


