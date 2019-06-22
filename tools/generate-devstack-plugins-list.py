#! /usr/bin/env python

# Copyright 2016 Hewlett Packard Enterprise Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script is intended to be run as part of a periodic proposal bot
# job in OpenStack infrastructure.
#
# In order to function correctly, the environment in which the
# script runs must have
#   * network access to the review.openstack.org Gerrit API
#     working directory
#   * network access to https://git.openstack.org/cgit

import functools
import logging
import json
import requests

logging.basicConfig(level=logging.DEBUG)

url = 'https://review.opendev.org/projects/'

# This is what a project looks like
'''
  "openstack-attic/akanda": {
    "id": "openstack-attic%2Fakanda",
    "state": "READ_ONLY"
  },
'''

def is_in_wanted_namespace(proj):
    # only interested in openstack or x namespace (e.g. not retired
    # stackforge, etc)
    if proj.startswith('stackforge/') or \
       proj.startswith('stackforge-attic/'):
        return False
    else:
        return True

# Check if this project has a plugin file
def has_devstack_plugin(session, proj):
    # Don't link in the deb packaging repos
    if "openstack/deb-" in proj:
        return False
    r = session.get("https://opendev.org/%s/raw/branch/master/devstack/plugin.sh" % proj)
    return r.status_code == 200

logging.debug("Getting project list from %s" % url)
r = requests.get(url)
projects = sorted(filter(is_in_wanted_namespace, json.loads(r.text[4:])))
logging.debug("Found %d projects" % len(projects))

s = requests.Session()
found_plugins = filter(functools.partial(has_devstack_plugin, s), projects)

for project in found_plugins:
    print(project)
