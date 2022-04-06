up:
	gunicorn wsgi:app --preload --bind 0.0.0.0:8080

up-dev:
	gunicorn wsgi:app --preload --bind 0.0.0.0:8080 --bind 0.0.0.0:8080 --reload

