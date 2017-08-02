#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SocialNetworkHarvester_v1p0.settings")

    from django.core.management import execute_from_command_line
    try:
        import SocialNetworkHarvester_v1p0.settings
    except:
        raise Exception("You must first set your own project settings, from the "+
                        "file 'clean_settings.py' located in SocialNetworkHarvester_1p0."+
                        " To do so, please copy the file 'clean_settings.py' and rename it to "+
                        "'settings.py' then edit it to reflect your own project.")
    execute_from_command_line(sys.argv)

