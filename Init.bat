call conda activate stock
python djangoapp/manage.py makemigrations
python djangoapp/manage.py migrate
python djangoapp/manage.py createsuperuser
python djangoapp/manage.py makemigrations stockapp
python djangoapp/manage.py migrate