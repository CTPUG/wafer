import sys

from setuptools import find_packages, setup

REQUIRES = [
    'Django>=1.6',
    'django-crispy-forms',
    'django-nose',
    'django-registration-redux',
    'pillow',
    'pyLibravatar',
    'pytz',
    'requests',
    'django-medusa>=0.3.0',
]

SOURCES = []

REQUIRES2 = [
    'pydns',
    # markdown 2.5 drops support for Python 2.6. Django 1.7 doesn't
    # support 2.6 either, so we can drop this restriction
    # when we move to Django 1.7
    'markdown<2.5',
    # We need django-markitup >= 2.2.2 to support django 1.7 properly
    # on python 2
    'django-markitup>=2.2.1',
]

SOURCES2 = []

REQUIRES3 = [
    'py3dns',
    'markdown>=2.5',
    'django-markitup>=2.2',
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

setup(
    name="wafer",
    version="0.3.0",
    url='http://github.com/CTPUG/wafer',
    license='MIT',
    description="A wafer-thin Django library for running small conferences.",
    long_description=long_description,
    author='CTPUG',
    author_email='ctpug@googlegroups.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIRES,
    dependency_links=SOURCES,
    setup_requires=[
        # Add setuptools-git, so we get correct behaviour for
        # include_package_data
        'setuptools_git >= 1.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
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
