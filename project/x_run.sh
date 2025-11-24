arg=$1
if [ "$arg" == "start" ]; then
    python manage.py runserver
elif [ "$arg" == "backend" ]; then
    pkill -f "python manage.py runserver"
    nohup python manage.py runserver 0.0.0.0:8001 > /dev/null 2>&1 &
elif [ "$arg" == "db" ]; then
    db_url=$2
    curl -o "db.sqlite3" '$db_url'
elif [ "$arg" == "clean" ]; then
    rm -f media/audio/*
fi