#!/bin/bash
#
# This ensures we run compile messages before we build the wheel

if [ ! -e ./manage.py ]; then
   echo "Please run this script in the base directory of the repository"
   exit 1
fi

# setuptools uses this to cache lookups for faster repeated builds, but that
# also leads to some unexpected results, so we ensure we're starting from a
# clean state
rm -rf wafer.egg-info
# Compile messages
./manage.py compilemessages
# Build the release files
python -m build

