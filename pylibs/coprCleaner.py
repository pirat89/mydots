
import os
import json
import sys
from datetime import datetime


import copr.v3


def get_owner_from_config():
    # We have just the name of project inside COPR_REPO value which is expected when the user
    # is the owner of the project. So set the user as owner from the config file.
    return client.config['username']

#ENV_VARS = {
#    '_COPR_CONFIG': '~/.config/copr',  # Copr config file. Get it through https://<copr instance>/api/.
#    'COPR_OWNER': None,  # Owner of the Copr project
#    'COPR_PROJECT': None,  # The Copr project to search
#    'COPR_PACKAGE': None,  # Name of the package to look for (any if not specified)
#    'COPR_REPO': None  # An alternative to COPR_OWNER & COPR_PROJECT. This env var should hold "owner/project".
#}
#
#
#for env, default in ENV_VARS.items():
#    ENV_VARS[env] = os.getenv(env, default)
#
#if projectname and not ownername:
#    ownername = get_owner_from_config()
#
#if not ownername or not projectname:
#    if not ENV_VARS['COPR_REPO']:
#        sys.stderr.write(
#            'Error: Use either COPR_REPO env var in a format "owner/project" or COPR_OWNER & COPR_PROJECT env vars to'
#            ' specify the Copr repository to search in.\n')
#        exit_fail()
#
#    if '/' in ENV_VARS['COPR_REPO']:
#        ownername, projectname = ENV_VARS['COPR_REPO'].split('/', 1)
#    else:
#        ownername = get_owner_from_config()
#        projectname = ENV_VARS['COPR_REPO']



CONFIG_PATH = os.path.expanduser("~/.config/copr_rh_oamg.conf")
if not os.path.exists(CONFIG_PATH):
    print("The COPR 'config' (API token) file not found: {}.".format(CONFIG_PATH), file=sys.stderr)
client = copr.v3.Client(copr.v3.config_from_file(path=CONFIG_PATH))
build_list = client.build_proxy.get_list(
    ownername=client.config['username'],
    projectname='leapp',
    pagination={'order': 'id', 'limit': None},
)
since_ts = datetime.timestamp(datetime.strptime("2020-06-01", "%Y-%m-%d"))
filtered_build_list = [i for i in build_list if i.submitted_on < since_ts]
builds_ids = [build.id for build in filtered_build_list]



# client.build_proxy.delete(24563)
