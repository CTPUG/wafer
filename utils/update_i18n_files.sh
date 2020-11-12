#!/bin/bash
# Update the langauge files and main django.pot file
LANGS="pt_BR ru"

base=$(dirname $0)
cd $base/..

for lang in $LANGS; do
   ./manage.py makemessages -l $lang
done
./manage.py makemessages --keep-pot
git status
