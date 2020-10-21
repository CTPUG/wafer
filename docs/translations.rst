Translations
============

Translating wafer
------------------

Translations for wafer are managed at `weblate.org`_

.. _weblate.org: https://hosted.weblate.org/projects/wafer/

Managing translations
---------------------

The summary is:

 * Add weblate as a remote
   ``git remote add weblate https://hosted.weblate.org/git/wafer/wafer/``

 * Pull weblate updates
   ``git remote update weblate``

 * Merge translations into wafer
   ``git merge weblate/master``

 * Fix any merge issues and create a PR on github

See the `weblate`_ documentation for more details on how to pull and merge translations.

To regenerate the django.pot file, use ``./manage.py makemessages --keep-pot``.


.. _weblate_ `https://docs.weblate.org/`


