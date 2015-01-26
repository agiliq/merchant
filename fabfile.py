from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ["merchant.agiliq.com"]
env.user = "agiliq"

def describe():
    print("This is a fab file to automate deployments for the merchant server.")

def deploy():
    with cd("/home/agiliq/envs/merchant/src/merchant"):
        run("git pull")

    with prefix("workon merchant"):
        with cd("/home/agiliq/envs/merchant/src/merchant/example"):
            run("pip install -r requirements.txt")
            run("python manage.py validate")
            run("python manage.py syncdb")

    run('/home/agiliq/scripts/merchant_restart.sh')
