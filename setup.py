from glob import glob
import subprocess
import sys

from setuptools import find_packages, setup

REQUIRES = [
    'Django>=1.11',
    'django-crispy-forms<1.9.0',
    'django-nose',
    'django-registration-redux',
    'djangorestframework<3.11',
    'drf-extensions<0.5',
    'jsonfield<3.0.0',
    'pillow',
    'diff-match-patch',
    'pyLibravatar',
    'pytz',
    'requests',
    'django-bakery>=0.12.0',
    'django-reversion>=2.0,<3.0.5',
    'django-select2',
    'django-markitup>=2.2.2',
    'markdown>=2.5',
    'icalendar>=4.0',
]

SOURCES = []

REQUIRES2 = [
    'pydns',
    'backports.csv',
]

SOURCES2 = []

REQUIRES3 = [
    'py3dns',
]

SOURCES3 = []

if sys.version_info < (3, 0):
    REQUIRES += REQUIRES2
    SOURCES += SOURCES2
else:
    REQUIRES += REQUIRES3
    SOURCES += SOURCES3

with open('README.rst', 'r') as f:
    long_description = f.read()


def compile_translations():
    try:
        subprocess.check_call(['./manage.py', 'compilemessages'])
    except subprocess.CalledProcessError:
        print("WARNING: cannot compile translations.")
        pass
    return glob('wafer/locale/*/LC_MESSAGES/django.mo')


setup(
    name="wafer",
    version="0.8.2a",
    url='http://github.com/CTPUG/wafer',
    license='ISC',
    description="A wafer-thin Django library for running small conferences.",
    long_description=long_description,
    author='CTPUG',
    author_email='ctpug@googlegroups.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIRES,
    dependency_links=SOURCES,
    data_files=compile_translations(),
    setup_requires=[
        # Add setuptools-git, so we get correct behaviour for
        # include_package_data
        'setuptools_git >= 1.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
