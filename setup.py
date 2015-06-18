# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name='django-comuni-italiani',
    packages=find_packages(),
    # package_data={'': ['']},
    include_package_data=True,
    version='1.0.1',
    install_requires=[
        'Django>=1.7',
    ],
    description='A simple django (>= 1.7) app for Italian cities and regions',
    author='Andrea Briganti',
    author_email='kbytesys@gmail.com',
    url='https://github.com/kbytesys/django_comuni_italiani',
    download_url='https://github.com/kbytesys/django_comuni_italiani/tarball/v1.0.1',
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
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

