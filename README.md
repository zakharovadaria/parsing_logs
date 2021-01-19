#### For up project:
    make start

#### For run tests
- you should have db on your local computer
- create db
- migrate db
- start tests `python manage.py test`

#### .env example
    DATABASE_URL=postgresql://<your_user>:<your_pass>@<path>:<port>/<database_name>
    TEST_DATABASE_URL=postgresql://<your_user>:<your_pass>@<path>:<port>/<database_name>
    CELERY_BROKER_URL=redis://<your_user>:<your_pass>@<path>:<port>/<db>
    SECRET_KEY=<your_secret_key>
    DEBUG=1
    ALLOWED_HOSTS=localhost
    POSTGRES_USER=<your_user>
    POSTGRES_PASSWORD=<your_pass
    POSTGRES_DB=<database_name>