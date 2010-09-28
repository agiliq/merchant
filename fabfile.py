from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ["merchant.agiliq.com"]
env.user = "agiliq"

def describe():
    print "This is a fab file to automate deployments for the merchant server."
   
def deploy():
    with cd("/home/agiliq/Work/merchant"):
        run("git pull")

    # with cd("/home/agiliq/Work/merchant/example"):
        # run("python manage.py validate")
        # run("python manage.py syncdb")

    # run("merchant-restart")
    run('/home/agiliq/scripts/restart_merchant.sh')
   
