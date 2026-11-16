# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()


version = '1.5.0'


setup(
    name='django-comuni-italiani',
    packages=find_packages(),
    # package_data={'': ['']},
    include_package_data=True,
    version=version,
    install_requires=[
        'Django>=3.2',
    ],
    description='A simple django (>= 3.2) app for Italian cities and regions, including the suppressed ones',
    long_description=readme(),
    long_description_content_type='text/markdown',
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
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

