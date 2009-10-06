#!/usr/bin/env python

import os, sys


DUMP_COMMAND = './manage.py dumpdata --format=json --indent=2 --remote %(app)s > fixtures/%(app)s.json'

APPS = 'auth registration feedback'.split()
if len(sys.argv) > 1:
    APPS = sys.argv[1:]


def system(command):
    print command
    status = os.system(command)
    if status:
        print "failed with exit code %d" % status
        sys.exit(status)


for app in APPS:
    system(DUMP_COMMAND % locals())
