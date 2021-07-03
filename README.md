# Musical Compass

## Development

### Project Setup

1. Make sure you have [pyenv](https://github.com/pyenv/pyenv) and [pipenv](https://github.com/pypa/pipenv) installed. `pyenv` will automatically set the required python version when you enter the directory
2. Create `.env` file
```bash
$ cp .env.example .env
```
3. Create a Spotify app and enter the Client ID and Secret into the `.env` file
4. Generate a secret key and insert it into the `.env` file. You can use the following code in a python console to retrieve one
```python
import os
os.urandom(24).hex()
```
6. Ensure that you have postgres installed and running on your local machine. If you are using the default `DATABASE_URL` value, you will need to create a postgres user called `admin` with the password `admin` and a database called `musical_compass`.
7. Install dependencies
```bash
$ pipenv install
```
3. Apply database migrations
```bash
$ pipenv run flask db upgrade
```

### Running locally

```bash
$ pipenv run gunicorn musical_compass:app
```
