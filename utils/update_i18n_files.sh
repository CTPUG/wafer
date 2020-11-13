#!/bin/bash
# Update the langauge files and main django.pot file

base=$(dirname $0)
cd $base/..

for cand in wafer/locale/*; do
   if [ ! -d $cand ]; then
      continue
   fi
   lang=$(basename $cand)
   ./manage.py makemessages -l $lang
done
./manage.py makemessages --keep-pot
git status
