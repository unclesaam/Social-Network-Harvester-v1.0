activate_this = '/PATH/TO/VIRTUAL/ENVIRONEMENT/bin/activate_this.py'
with open(activate_this) as file:
    exec(file.read(), dict(__file__=activate_this))

import os
import sys

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
dname = os.path.join(dname,'..')
sys.path.insert(0,dname)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SocialNetworkHarvester_v1p0.settings")
application = get_wsgi_application()  