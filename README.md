# Social-Network-Harvester-v1.0

How to install the SNH on Ubuntu server v.14.04.4:

1. Install the prerequisites:
  - sudo apt-get update
  - sudo apt-get upgrade
  - sudo apt-get install python3-dev libmysqlclient-dev python-pip

2. Create a virtual environnement for python:
  - pip install virtualenv
  - sudo virtualenv py3env -p python3
  - source py3env/bin/activate

3. Install python3 modules:
  - pip install mysqlclient
  - pip install django

4. run the server in dev-mode:
  - cd Social-Network-Harvester-v1.0/Social-Network-Harvester-v1.0
  - python manage.py runserver 
