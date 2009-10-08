#!/usr/bin/env python

import os, sys

APPS = 'auth registration feedback suggestions tags'.split()

DUMP_COMMAND = ' '.join("""
./manage.py dumpdata
--format=json --indent=2 --remote %(app)s
> fixtures/%(app)s.json
""".split())


def system(command):
    print command
    status = os.system(command)
    if status:
        print "failed with exit code %d" % status
        sys.exit(status)


def main(argv):
    apps = APPS
    if len(argv) > 1:
        apps = argv[1:]
    for app in apps:
        system(DUMP_COMMAND % locals())


if __name__ == '__main__':
    main(sys.argv)
