# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def readme():
    with open('README.txt') as f:
        return f.read()


version = '1.4.1'


setup(
    name='django-comuni-italiani',
    packages=find_packages(),
    # package_data={'': ['']},
    include_package_data=True,
    version=version,
    install_requires=[
        'Django>=1.7',
    ],
    description='A simple django (>= 1.7) app for Italian cities and regions',
    long_description=readme(),
    author='Andrea Briganti',
    author_email='kbytesys@gmail.com',
    url='https://github.com/kbytesys/django_comuni_italiani',
    download_url='https://github.com/kbytesys/django_comuni_italiani/tarball/v1.3.0',
    keywords=['django', 'comuni', 'regioni', 'province'],
    license='GNU LGPL v2',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: Italian',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

