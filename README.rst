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
