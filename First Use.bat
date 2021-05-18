call conda activate stock
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py makemigrations stockapp
python manage.py migrate