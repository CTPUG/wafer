from glob import glob
import subprocess
import sys

from setuptools import find_packages, setup

REQUIRES = [
    'Django>=1.11',
    'django-crispy-forms',
    'django-nose',
    'django-registration-redux',
    'djangorestframework',
    'drf-extensions>=0.5.0',
    'jsonfield',
    'pillow',
    'diff-match-patch',
    'pyLibravatar',
    'pytz',
    'requests',
    'django-bakery>=0.12.0',
    'django-select2',
    'django-reversion',
    'markdown>=2.5',
    'icalendar>=4.0',
    'py3dns',
    'django-markitup>=4.0.0',
]

SOURCES = []


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
    version="0.9.1",
    url='http://github.com/CTPUG/wafer',
    license='ISC',
    description="A wafer-thin Django library for running small conferences.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
