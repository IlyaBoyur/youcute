# Youcute: Social network for pet owners
* Developed with MVC architecture
* Implemented: pagination, landing page cache, JOIN requests.
* Registration verification.
* Password change/recovery via e-mail
* Service functionality tests (Django unittests)
Tech Stack: Python 3, Django, Bootstrap, SQLite3, pytest, unittest

<br>

To test functionality:
### 1. Prepare workspace
In project folder:
```bash
python -m venv venv
source venv/bin/activate # Windows (Git Bash/WSL): source venv/Scripts/activate
pip install -r requirements.txt
```
### 2. Create project database and migrate it
```bash
python manage.py migrate
```
### 3. Create admin user
```bash
echo "from django.contrib.auth.models import User" > createadmin.py
echo "User.objects.create_superuser('admin', 'admin@example.io', 'admin')" >> createadmin.py
python manage.py shell < createadmin.py
```
### 4. Start the app
```bash
python manage.py runserver
```
### 5. Enjoy!
Project is avaliable on http://127.0.0.1:8000/

Examine Django Admin with user=admin, password=admin here: http://127.0.0.1:8000/admin
