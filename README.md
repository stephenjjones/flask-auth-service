# Auth Service

### Status
Work in Progress

### Description
A auth server implementation in Flask, SQL-alchemy, postgres, and argon2 password hashing.

This is a purposefully minimal auth server to be used in a microservice architecture

### Components
Flask
Postgres
SQL-Alchemy
argon2

### FAQ
Q: How to create database tables?
```
$ python server.py shell
>>> from server import db
>>> db.create_all()
```
  

### Setup local dev: OSX
Get updated python:
```
$ brew update
$ brew install python3
$ python3 --version
$ pyvenv env
$ source env/bin/activate
$ pip install --upgrade pip
```

Install dependencies
`$ pip install -r requirements.txt`

or

```
$ pip install flask
$ pip install psycopg2
$ pip install flask-script
$ pip install flask-sqlalchemy
# http://argon2-cffi.readthedocs.io/en/stable/installation.html
$ pip install argon2_cffi
$ pip install flask-httpauth
$ pip install marshmallow
$ pip install flask-migrate
```

Setup database:

```
$ brew update
$ brew install postgresql
$ which psql # confirm proper installation at /usr/local/bin/psql
$ postgres -D /usr/local/var/postgres # start postgres server
$ createdb 'whoami' # create a default db based on your username
$ psql
=# CREATE DATABASE yourdbname OWNER yourdbuser ENCODING 'UTF8'
OR
=# CREATE DATABASE yourdbname
=# CREATE USER myprojectuser WITH PASSWORD 'password';
=# ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
=# ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
=# ALTER ROLE myprojectuser SET timezone TO 'UTC';
=# GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
=# \q
```

Migrations
```
$ python server.py db migrate -m "initial migration"
$ python server.py db upgrade
```

### Models
* Users
  - id (primary key)
  - email
  - passwordHashed
  - role_id (M2M)
* Roles
  - id (primary key)
  - name

#### Reference links
[Flask web apis](http://blog.miguelgrinberg.com/post/restful-authentication-with-flask)
[hynek](https://hynek.me/articles/storing-passwords/)
[flask restful api services](https://www.youtube.com/watch?v=px_vg9Far1Y)
[marshmallow serialization and validation](http://marshmallow.readthedocs.io/en/latest/)
