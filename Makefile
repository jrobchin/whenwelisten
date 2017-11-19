serve:
	gunicorn --env DJANGO_SETTINGS_MODULE=livesmatter.settings livesmatter.wsgi -w 2 -b 0.0.0.0:80
