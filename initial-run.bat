pip install -r requirements.txt
cd project
python manage.py migrate
python manage.py loaddata data.json
python manage.py collectstatic
python manage.py runserver