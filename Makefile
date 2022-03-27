up:
	gunicorn --bind 0.0.0.0:8080 wsgi:app

up-dev:
	gunicorn --bind 0.0.0.0:8080 --reload wsgi:app

