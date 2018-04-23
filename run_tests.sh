#!/bin/sh

# use /media/ when running (travis) tests
echo 'THUMBNAIL_URL = "/media/"' > ocd_frontend/travis_settings.py
#nosetests -l debug --nocapture --with-coverage --cover-package=ocd_backend,ocd_frontend --cover-inclusive
nosetests --with-coverage --cover-package=ocd_backend,ocd_frontend --cover-inclusive
TEST_EXIT_VAL=$?
rm -f ocd_frontend/travis_settings.py
exit $TEST_EXIT_VAL
