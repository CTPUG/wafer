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
    'django-medusa',
]

SOURCES = []

REQUIRES2 = [
    'pydns',
    # markdown 2.5 drops support for Python 2.6. Django 1.7 doesn't
    # support 2.6 either, so we can drop this restriction
    # when we move to Django 1.7
    'markdown<2.5',
    # markitup 2.2 breaks on python 2 with module level imports, which we
    # need to use for markdown, so avoid using that
    'django-markitup<=2.1',
]

SOURCES2 = []

REQUIRES3 = [
    'py3dns',
    'markdown>=2.5',
    'django-markitup>=2.2',
]

SOURCES3 = [
    # Until Pyton3 support is merged to master, use this branch
    'https://github.com/kezabelle/django-medusa/archive/44d82054d39b794033e5df25fd9e630d05c97f3b.zip#egg=django-medusa-0.2.1',
]

if sys.version_info < (3, 0):
    REQUIRES += REQUIRES2
    SOURCES += SOURCES2
else:
    REQUIRES += REQUIRES3
    SOURCES += SOURCES3

setup(
    name="wafer",
    version="0.1.0a",
    url='http://github.com/CTPUG/wafer',
    license='MIT',
    description="A wafer-thin Django library for running small conferences.",
    long_description=open('README.md', 'r').read(),
    author='CTPUG',
    author_email='ctpug@googlegroups.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIRES,
    dependency_links=SOURCES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
        'Programming Language :: Python :: 3.3'
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
