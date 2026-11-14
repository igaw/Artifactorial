#!/bin/sh

[ -n "$1" ] && exec "$@"

#########################
# wait for the database #
#########################
check_database() {
    python3 manage.py shell -c "import sys
from django.db import connections
try:
  connections['default'].cursor()
except Exception:
  sys.exit(1)
sys.exit(0)"
}

wait_database() {
    until check_database
    do
        printf "."
        sleep 1
    done
}


# Fail fast on configuration errors (e.g. no SECRET_KEY) instead of looping
# forever below; the system checks don't need the database.
python3 manage.py check || exit 1

echo "Waiting for the database"
wait_database
echo "done"
echo ""
echo "Applying migrations"
python3 manage.py migrate --noinput
echo "done"
echo ""

exec gunicorn --log-level debug --bind 0.0.0.0:80 --threads 10 --workers 4 --worker-tmp-dir /dev/shm website.wsgi
