"""meme_get setup.py"""
from os import path
from setuptools import setup, find_packages

PACKAGE_NAME = 'meme_get'
HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    README = f.read()


setup(name=PACKAGE_NAME,
      version='1.0.0b1',
      description='Get memes',
      long_description=README,
      license='MIT',
      author='Jingnan Shi',
      author_email='jshi@g.hmc.edu',
      url='https://github.com/memegen/meme_get',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Topic :: Utilities'
      ],
      keywords=['meme', 'client', 'download'],
      install_requires=[
          'beautifulsoup4',
          'requests',
          'pyenchant',
          'praw',
          'lxml',
          'Pillow'],
      packages=find_packages(exclude=['tests', 'tests.*']),
      package_data={
          '':['LICENSE', '*.rst', '*.txt', '*.ini', '*.data', '*.ttf', '*.cfg']
      })
