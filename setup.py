from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name="wafer",
    version="0.2.0a",
    url='http://github.com/CTPUG/wafer',
    license='MIT',
    description="A wafer-thin Django library for running small conferences.",
    long_description=long_description,
    author='CTPUG',
    author_email='ctpug@googlegroups.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.6',
        'django-crispy-forms',
        'django-nose',
        'django-registration-redux',
        'pillow',
        'pyLibravatar',
        'pydns',
        'pytz',
        'requests',
        # markdown 2.5 drops support for Python 2.6. Django 1.7 doesn't
        # support 2.6 either, so we can drop this restriction
        # when we move to Django 1.7
        'markdown<2.5',
        'django-medusa',
        # markitup 2.2 breaks on python 2 with module level imports, which we
        # need to use for markdown, so avoid using that
        'django-markitup<=2.1,>2.2',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
