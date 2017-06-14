# JukifyService
A Group Recommendation API for Spotify

## Development Setup

### Pre-requisites

* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli): download and [install](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)
* Python version 3.6, Setuptools and pip installed locally - see the installation guides for [OS X](http://docs.python-guide.org/en/latest/starting/install3/osx/), [Windows](http://docs.python-guide.org/en/latest/starting/install3/win/), and [Linux](http://docs.python-guide.org/en/latest/starting/install3/linux/).
* [Virtualenv](https://github.com/kennethreitz/python-guide/blob/master/docs/dev/virtualenvs.rst): `pip install virtualenv`
* Postgres [installed locally](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup)

### Setting up

```sh
git clone https://github.com/jukify/jukify-service
cd jukify-service
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
python manage.py collectstatic
```

#### Heroku

```sh
heroku login
heroku local web
```

Open http://localhost:5000 with your web browser. You should see your app running locally