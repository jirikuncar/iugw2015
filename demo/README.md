### Adding the Flask-IIIF and basic Jinja 2 formating

Hello, I'm Harris and working mostly on CDS multimedia, and with this presentation
we'll extend Jiri's tutorial and add templates using Jinja and configure
Flask-IIIF extension.

Not many people have images in their instances, but for those who does how many
subformats have for each?

Wouldn't be better to keep only the original and generate when need it
any other version? With the help of International Image Interoperability
Framework it's really easy. We implemented the `Image API` spec in the
`Flask-IIIF` extension. And you can manipulate images through a powerful
RESTful API. Let's have a quick look:

Demo: `https://flask-iiif.herokuapp.com/restful`

OK! Let's install Flask-IIIF first.

In `requirements.txt` add the following:

```txt
Flask-IIIF>=0.2.0
```
and then run

```bash
$ pip install -r requirements.txt
```

Flask-IIIF supports a UUID (universally unique identifier) opener function
which allows you to open an image either with fullpath or Bytestream.
This means you can import any existing filemanager such as `Amazon S3`.

So let's assume for our example that the filemanager is our filesystem under
the application directory `./images`

Now let's update our application to support Flask-IIIF,  In the `app.py`

```python
from flask import render_template

from flask_iiif import IIIF
from flask_restful import Api

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

@app.route('/image/<string:name>')
def formated(name):
  return render_template("image.html", name=name)
```

Now we need to create the template let's create a `./templates/image.html`

```bash
$ mkdir templates
$ cd templates
$ vim image.html
```

```html
<img src="{{ iiif_image_url(uuid=name, size="200,200") }}" />
```

One more step! Add some images to `./images/`

```bash
$ mkdir images
$ cd images
$ wget http://flask-iiif.herokuapp.com/static/images/native.jpg
```
*(Note the image used on this demo is 7800x8300)*

*For the `docker` users you may need to rebuild the `web` container*
```bash
$ docker build -t web .
```

Now open your browser to `http://localhost:5000/image/native.jpg`

You can also change paremeters directly with the restful api.

Rotate: `http://localhost:5000/api/multimedia/image/v2/native.jpg/full/500%2C500/90/default.png`  
Bitonal: `http://localhost:5000/api/multimedia/image/v2/native.jpg/full/500%2C500/0/bitonal.png`  
Crop: `http://localhost:5000/api/multimedia/image/v2/native.jpg/500,500,1500,1500/full/0/default.png`  
All together: `http://localhost:5000/api/multimedia/image/v2/native.jpg/500,500,300,300/300,300/90/bitonal.png`

---

#### Docker notes
```bash
$ docker build -t web .
$ docker-machine create -d virtualbox dev
$ eval "$(docker-machine env dev)"
$ docker-compose up -d
$ docker run -d --name=example -p 5000:5000 web
$ open "http://`docker-machine ip dev`:5000"
```
#### Trubleshooting

```bash
$ docker stop $(docker ps -a -q)
$ docker build -t web .
$ docker-compose up -d
$ docker-compose ps
```
