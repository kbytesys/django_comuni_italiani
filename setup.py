__author__ = 'kbyte'
from distutils.core import setup
setup(
    name='django-comuni-italiani',
    packages=['comuni_italiani'],
    version='1.0',
    description='A simple django (>= 1.7) app for Italian cities and regions',
    author='Andrea Briganti',
    author_email='kbytesys@gmail.com',
    url='https://github.com/kbytesys/django_comuni_italiani',
    download_url='https://github.com/kbytesys/django_comuni_italiani/tarball/1.0.0',
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

