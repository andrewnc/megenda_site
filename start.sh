export FLASK_APP=run.py
export FLASK_CONFIG=development
pg_ctl -D /usr/local/var/postgres start
flask run