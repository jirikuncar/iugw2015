import datetime
import os
import json
import zlib

from celery import Celery
from flask import Flask, jsonify, request, render_template
from flask_iiif import IIIF
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from sqlalchemy_utils.types.json import JSONType

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/test.db'
)
db = SQLAlchemy(app)
redis = Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)
celery = Celery('app', broker=os.environ.get(
    'CELERY_BROKER_URL', 'redis://localhost:6379'
))

# Init the iiif extension
iiif = IIIF(app=app)
# Init the restful api
api = Api(app=app)
# Init restful api to flask-iiif
iiif.init_restful(api)


# Where iiif will find the images in our case `./images`
def uuid_to_source(uuid):
    image_path = os.path.join('./', 'images')
    return os.path.join(image_path, uuid)

# Init the opener function
iiif.uuid_to_image_opener_handler(uuid_to_source)

# Initialize the cache
app.config['IIIF_CACHE_HANDLER'] = redis


@celery.task()
def make_sip(recid, data):
    now = datetime.datetime.now().isoformat()
    with open('./{0}_{1}.zip'.format(recid, now), 'wb') as f:
        f.write(zlib.compress(json.dumps(data).encode('utf-8')))


class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    json = db.Column(JSONType)


@app.route("/")
def hello():
    redis.incr('hits')
    return 'I have been seen {0} times.'.format(int(redis.get('hits')))


@app.route("/record", methods=['POST'])
def add():
    data = json.loads(request.data.decode('utf-8'))
    record = Record(json=data)
    db.session.add(record)
    db.session.commit()
    make_sip.delay(record.id, data)
    return jsonify(id=record.id, data=record.json)


@app.route("/record", methods=['GET'])
def list():
    return jsonify(results=[
        dict(id=r.id, data=r.json) for r in Record.query.all()
    ])


@app.route('/image/<string:name>')
def formated(name):
    return render_template("image.html", name=name)


if __name__ == "__main__":
    # We simply try to create database.
    try:
        db.create_all()
    except Exception:
        app.logger.exception('Please check that your database is running.')
    # We run in debug mode on port 5000.
    app.run(host="0.0.0.0", port=5000, debug=True)
