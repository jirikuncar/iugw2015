==================================
 Invenio User Group Workshop 2015
==================================

*Jiri Kuncar <jiri.kuncar@cern.ch>*

Invenio 2 Technology Background
===============================

We will have a look closely on technologies used in Invenio 2.x. We will
build and deploy our simple application with webserver, database, cache,
workers and message queue using Docker.

0. What do I need on my machine?
--------------------------------

During the whole introductory section we will work with **Docker**.

.. image:: https://www.docker.com/sites/all/themes/docker/assets/images/logo.png
   :target: https://www.docker.com/

Please follow this `link <https://www.docker.com/>`_ and install Docker
tool chain on your machine. When you are done please verify versions of
your binaries.

.. code-block:: console

    $ brew update && brew install docker docker-compose docker-machine
    $ docker --version
    Docker version 1.8.2, build 0a8c2e3
    $ docker-compose --version
    docker-compose version: 1.4.2
    $ docker-machine --version
    docker-machine version 0.4.1 (HEAD)

**Did you miss anything?** Check it on GitHub at
`<https://github.com/jirikuncar/iugw2015>`_.

*If you find any typo or error, please fork it and submit a PR.*

1. Build your Flask application
-------------------------------

The outcome of this section should be running Flask application in your
Docker machine.

Flask
~~~~~

We can start by copy and pasting example from *Flask* homepage.

.. imgae:: http://flask.pocoo.org/static/logo/flask.png
    :target: http://flask.pocoo.org/

.. code-block:: python

    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "Hello World!"

    if __name__ == "__main__":
        app.run()


You can find the application in ``./example/app.py``. For running this
example we need to install ``Flask`` dependecy. The fastest way is to use
``pip install Flask``. To help the automatization process we add
``Flask>=0.10.1`` to ``./example/requrements.txt``.

*Imatient students can try it on their own machine (in new virtualenv).*

.. code-block:: console

    # mkvirtualenv iugw2015
    $ pip install -r example/requirements.txt
    $ python example/app.py

How do we automatize this environment creation and make it repeatable?

Dockerfile
~~~~~~~~~~

Now, create a configuration specifying all dependencies for creating your
Docker image.

.. code-block:: text

    FROM python:3.5
    ADD . /code
    WORKDIR /code
    RUN pip install -r requirements.txt
    CMD python app.py

We build an image starting with the Python 3.5 image. The next command adds the
current directory ``.`` into the path ``/code`` in the image. Then we set the
working directory to ``/code``. In next step we will take advantage of
previously created ``requirements.txt`` file with our Python dependencies. The
last step is to set the default command for the container run when started to
``python app.py``.

If you have done everything correctly, you can build the image by running
``docker build -t web .``.

We have our image and now we need a machine to run it.

.. code-block:: console

    $ docker-machine create -d virtualbox dev
    $ eval "$(docker-machine env dev)"
    $ docker run -d --name=example -p 5000:5000 web
    $ open "http://`docker-machine ip dev`:5000"

Do you have a problem?

- Check that your docker machine is running ``docker-machine ls``.
- Check that your docker image is running ``docker ps``.

2. Compose services
-------------------

The goal of this section is to extend our application to use multiple services
and configure deployment it using ``docker-compose``.

Let's start with configuring a Redis service. We will need to add
``redis`` to ``requirements.txt`` and modify our ``app.py``.

.. code-block:: python

    import os
    from redis import Redis
    redis = Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)

Please note that we use environment variable ``REDIS_HOST`` to ease
linking of services specified in ``docker-compose.yml``.

docker-compose.yml
~~~~~~~~~~~~~~~~~~

Following configuration automatize builing of ``web`` node and creates
link with ``redis``. We are going to use ``redis`` image from Docker Hub
registry.

.. code-block:: text

    web:
      build: .
      ports:
       - "5000:5000"
      volumes:
       - .:/code
      links:
       - redis
      environment:
       - REDIS_HOST=redis
    redis:
      image: redis

*Check that you have ``docker-compose.yml`` in the same directory as
``Dockerfile``.*

Now you can start your start the machines using ``docker-compose up``
and check that your application is available on the same url
*"http://`docker-machine ip dev`:5000"*.

You should get a message in your browser saying:

``I have been seen 1 times.``

We have checked that everything is up-and-running so we can keep the
services running in the background using ``-d`` option.

.. code-block:: console

    $ docker-compose up -d
    Starting example_redis_1...
    Starting example_web_1...
    $ docker-compose ps
         Name                   Command             State           Ports
    ------------------------------------------------------------------------------
    example_redis_1   /entrypoint.sh redis-server   Up      6379/tcp
    example_web_1     /bin/sh -c python app.py      Up      0.0.0.0:5000->5000/tcp


**Q: How can I check the logs?**

*A: You can use ``docker-compose logs`` to see logs from all machines or
just ``docker-compose logs redis`` if you want to see logs from ``redis``
one.*

Database
~~~~~~~~

In order to simplify our excercise we will take advantage of some excelent
libraries:

- ``SQLAlchemy`` provides database ORM;
- ``SQLAlchemy-Utils`` hides some implementation details;
- ``Flask-SQLAlchemy`` provides integration with ``Flask`` application.

Please include them in your ``requirements.txt``.

In the next step we define your shared database object and first model.

.. code-block:: python

    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy_utils.fields import JSONField

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/test.db'
    )
    db = SQLAlchemy(app)


    class Record(db.Model):
        __tablename__ = 'record'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        json = db.Column(JSONField)


**Q: How do I create the database tables?**

*A: In our demo we will try to create database tables everytime we start the
application using ``db.create_all()``.*

If you try to run the script now it will create new SQLite database in
``/tmp/test.db``. Better way is to use external database service or new
image with database of your choice and make the plumbing using
``docker-compose``.

In this tutorial we will show the integration with default image of
*Postgres* database from Docker Hub.

- Add new image ``db: postgres`` and link ``web`` with ``db``;
- Include new environment variable for ``web`` with following value
  ``SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@db:5432/postgres``;
- Include ``psyconpg2`` in ``requirements.txt``.

Please build and restart your ``docker-compose`` daemon. It will pull
latest ``postgres`` image and setup your application to use it instead of
*SQLite*.

Now it is time to implement some simple REST API for your ``Record``
model.

.. code-block:: python

    @app.route("/record", methods=['POST'])
    def add():
        data = json.loads(request.data.decode('utf-8'))
        record = Record(json=data)
        db.session.add(record)
        db.session.commit()
        return jsonify(id=record.id, data=record.json)


    @app.route("/record", methods=['GET'])
    def list():
        return jsonify(results=[
            dict(id=r.id, data=r.json) for r in Record.query.all()
        ])


When you safe ``app.py`` check that the application server has been
reloaded.

*Uploading new record:*

.. code-block:: console

    $ curl -H "Content-Type: application/json" -X POST \
    -d '{"title": "Test"}' http://`docker-machine ip dev`:5000/record
    {
      "data": {
        "title": "Test"
      },
      "id": 1
    }

*Retrieving all records*

.. code-block:: console

    $ curl http://`docker-machine ip dev`:5000"/record
    {
      "results": [
        {
          "data": {
            "title": "Test"
          },
          "id": 1
        }
      ]
    }


2. Scaling your application
---------------------------

In this section we will briefly show how to scale and optimize your newly
created application.

.. code-block:: console

    $ docker-compose scale web=4

It is almost so simple however we need to add a *proxy* in front of our
``web`` service and patch the plumbing.

.. code-block:: text

    haproxy:
      image: tutum/haproxy
      environment:
      - PORT=5000
      links:
      - web
      ports:
      - "80:80"
    ...
    web:
      ports:
       - "5000"
    ...

After rebuilding and starting services you can look inside logs
``docker-compose logs`` to see how the individual servers are used.

Tuning ``Dockerfile``
~~~~~~~~~~~~~~~~~~~~~

In order to take advantage of Docker image caches we can refactor
your ``Dockerfile`` so the installed requirements are cached.

.. code-block:: text

    FROM python:3.5
    ENV PYTHONUNBUFFERED 1
    RUN mkdir /code
    WORKDIR /code
    ADD requirements.txt /code/
    RUN pip install -r requirements.txt
    ADD . /code/

To improve reusability of our ``web`` image we have removed automatic
server startup and added to ``docker-compose.yml`` configuration.

.. code-block:: text

    web:
       command: python app.py


The above changes allow us to integrate task queue system for heavy
computation.

Worker
~~~~~~

Generally it is good idea to offload time consuming tasks from request handlers
to keep the response time low.  One can use `Celery
<http://www.celeryproject.org/>`_ for asynchronous task queue/job queue.

First, we define a function that take record id and data and stores it in ZIP
file.

.. code-block:: python

    import datetime
    import zlib
    from celery import Celery

    celery = Celery('app', broker=os.environ.get(
        'CELERY_BROKER_URL', 'redis://localhost:6379'
    ))


    @celery.task()
    def make_sip(recid, data):
        now = datetime.datetime.now().isoformat()
        with open('./{0}_{1}.zip'.format(recid, now), 'wb') as f:
            f.write(zlib.compress(json.dumps(data).encode('utf-8')))


The decorator ``@celery.task()`` registers ``make_sip`` function as task in
*Celery* application.  We should not forget to add ``celery`` package to
``requirements.txt``.

Next step is to update our ``docker-compose.yml`` with new ``worker`` node
and include ``CELERY_BROKER_URL=redis://redis:6379`` in our ``web`` node.

.. code-block:: text

    worker:
      build: .
      command: celery -A app.celery worker -l INFO
      volumes:
       - .:/code
      links:
       - db
       - redis
      environment:
       - REDIS_HOST=redis
       - CELERY_BROKER_URL=redis://redis:6379
       - SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@db:5432/postgres


Please note that because ``celery`` should not run under ``root`` user, we
need to update ``Dockerfile``.

.. code-block:: text

    ...
    RUN useradd --home-dir /home/demo --create-home --shell /bin/bash --uid 1000 demo
    ...
    USER demo


Now you should be able to run your application. In case you have many requests
you can increase number of running workers.

.. code-block:: console

    $ docker-compose scale worker=2
