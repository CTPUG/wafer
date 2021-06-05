#!/bin/bash
# Update the langauge files and main django.pot file

base=$(dirname $0)
cd $base/..

# Create a root-level locale directory, that we'll ignore.
# This is used for anything outside wafer (e.g. docs)
# makemessages searches all files under the current directory, and we want to
# prefix our filenames with wafer/
mkdir -p locale

for cand in wafer/locale/*; do
   if [ ! -d $cand ]; then
      continue
   fi
   lang=$(basename $cand)
   ./manage.py makemessages -l $lang
done
./manage.py makemessages --keep-pot
git status
