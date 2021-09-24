from glob import glob
import subprocess

from setuptools import find_packages, setup

REQUIRES = [
    'Django>=2.2,<3.1',
    'bleach',
    'bleach-allowlist',
    'diff-match-patch',
    'django-bakery>=0.12.0',
    'django-crispy-forms',
    'django-markitup>=4.0.0',
    'django-nose',
    'django-registration-redux',
    'django-reversion',
    'django-select2',
    'djangorestframework',
    'drf-extensions>=0.5.0',
    'icalendar>=4.0',
    'jsonfield',
    'markdown>=2.5',
    'pillow',
    'py3dns',
    'pyLibravatar',
    'pytz',
    'requests',
]

SOURCES = []


with open('README.rst', 'r') as f:
    long_description = f.read()


def compile_translations():
    try:
        subprocess.check_call(['./manage.py', 'compilemessages'])
    except subprocess.CalledProcessError:
        print("WARNING: cannot compile translations.")
    return glob('wafer/locale/*/LC_MESSAGES/django.mo')


setup(
    name="wafer",
    version="0.12.0",
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
