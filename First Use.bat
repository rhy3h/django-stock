call conda activate stock
python stockapp/manage.py makemigrations
python stockapp/manage.py migrate
python stockapp/manage.py createsuperuser
python stockapp/manage.py makemigrations stockapp
python stockapp/manage.py migrate