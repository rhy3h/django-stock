git pull
call conda activate stock
start http://127.0.0.1:8010/broker-group
python djangoapp/manage.py runserver 127.0.0.1:8010