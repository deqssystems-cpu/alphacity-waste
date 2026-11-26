# Alphacity Waste Management (Django + HTMX)
Oyugis Town, Homa Bay County · Licensed by the County Government of Homa Bay
Tel +254 795 624 278 · alphacitywaste@gmail.com · Built by Deqs Systems (www.deqssystems.app)

## Run
    python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations core
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
Site: http://127.0.0.1:8000/ · Staff login: /login/ · Advanced admin: /django-admin/

## Features
Public website · admin login · dashboard · client registration · monthly payments · printable receipts ·
expenses · income vs expenses reports · bin supply records · enquiries inbox · CSV exports.
Photos: your own images are in static/img; stock photos are listed in core/images.py (Unsplash, live links).
For production set SECRET_KEY, DEBUG=0, ALLOWED_HOSTS and run `collectstatic`.
