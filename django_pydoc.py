import os
import django
import pydoc


# Prepare Django before executing pydoc command
os.environ['DJANGO_SETTINGS_MODULE'] = 'sga.settings' # Change the value according to your django settings path
django.setup()

# Now executing pydoc
pydoc.cli()
