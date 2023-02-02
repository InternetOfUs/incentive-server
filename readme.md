# WeNet Incentive server
## Introduction
This component responsible for allowing WeNet applications to incentive WeNet users and WeNet communities.
It exposes dedicated endpoints allowing to manage:

* message based incentives 
* badges based incentives
* creating  issuers, badges_types and badges thru the platform.

## Installation

### Docker support

#### Requirements:
docker and docker-compose are required to be installed on the host machine. 
for installation details on ubuntu 18.04 please visit digital ocean great tutorial: 

[Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)

[docker-compose](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04)
### Build and running
A dedicated Docker images for this component can pull  from DockerHub thru Docker-compose.
The command:
```bash
docker-compose up 
```
Will create and run  :

* Mysql server on port 3306   with two databases:
    * DataBase named lassi for the incentive server 
    * DataBase named libraries for the Badgr server

* phpMyAdmin server on port 8080 
* The incentive sever on port 80 (default)
* Badgr server on port 8000
* additional crontab server to schedule process and nginx to serve the servers on production.
## Required env variables
The following environmental variables are required to change in .env file  for the component to run properly.
### badgrserver
* BASE_URL
* MYSQL_DATABASE
* MYSQL_ROOT_PASSWORD
* MYSQL_PASSWORD
* MYSQL_USER
* Badger_TOKEN
* BADGR_HTTP_ORIGIN
* DB
* UPLOAD_LIMIT
* DEBUG
### incentiveserver
* S3
* BASE_URL
* ENVIRONMENT
* MYSQL_DATABASE
* MYSQL_USER
* MYSQL_ROOT_PASSWORD
* MYSQL_PASSWORD
* Badger_TOKEN
* DB
* UPLOAD_LIMIT
* BADGR_DOMAIN
* INCENTIVE_SERVER_DEBUG
* COMP_AUTH_KEY


## Documentation

The APIs documentation is available [here](http://swagger.u-hopper.com/?url=https://bitbucket.org/wenet/wenet-components-documentation/raw/master/sources/wenet-incentive-server-api.json).


## Postman collection

The Postman Collection with full address of the Incentive server APIs, Created for you to test the APIs easily before you implement it at your side. 
The incentive server is dockerized and up to air at https:/www.internetofus.eu.
Please do not hesitate to contact us for any question.

# Contact us
  - Daniel izmaylov@post.bgu.ac.il
  - Avi avisegal@gmail.com

