#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install


class InstallWrapper(install):
    def run(self):
        self._download_spacy_es()
        self._download_spacy_affixes_es()
        install.run(self)

    def _download_spacy_es(self):
        from spacy.cli import download
        download('es_core_news_md')

    def _download_spacy_affixes_es(self):
        from spacy_affixes.utils import download
        download(lang='es')


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setup(
    name='rantanplan',
    version='0.2.0',
    license='Apache Software License 2.0',
    description='Scansion tool for Spanish texts',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='LINHD POSTDATA Project',
    author_email='info@linhd.uned.es',
    url='https://github.com/linhd-postdata/rantanplan',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://rantanplan.readthedocs.io/',
        'Changelog': 'https://rantanplan.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/linhd-postdata/rantanplan/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=read('requirements.txt').splitlines(),
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'rantanplan = rantanplan.cli:main',
        ]
    },
    cmdclass={
        'install': InstallWrapper
    }
)
