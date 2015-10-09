import os

from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)


@app.route("/")
def hello():
    redis.incr('hits')
    return 'I have been seen {0} times.'.format(int(redis.get('hits')))

if __name__ == "__main__":
    # We run in debug mode on port 5000.
    app.run(host="0.0.0.0", port=5000, debug=True)
