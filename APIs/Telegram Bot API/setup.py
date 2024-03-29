#!/usr/bin/env python
from setuptools import setup, find_packages
from io import open
import re

def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()

with open('telebot/version.py', 'r', encoding='utf-8') as f:  # Credits: LonamiWebs
    version = re.search(r"^__version__\s*=\s*'(.*)'.*$",
                        f.read(), flags=re.MULTILINE).group(1)

setup(name='pyTelegramBotAPI',
      version=version,
      description='Python Telegram bot api. ',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      author='mavdian',
      author_email='michaelavdian14@gmail.com',
      url='https://github.com/mavdian14/portfolio/TelegramBotAPI',
      packages = find_packages(exclude = ['tests', 'examples']),
      license='GPL2',
      keywords='telegram bot api tools',
      install_requires=['requests'],
      extras_require={
          'json': 'ujson',
          'PIL': 'Pillow',
          'redis': 'redis>=3.4.1',
          'aioredis': 'aioredis',
          'aiohttp': 'aiohttp',
          'fastapi': 'fastapi',
          'uvicorn': 'uvicorn',
          'psutil': 'psutil',
          'coloredlogs': 'coloredlogs',
          'watchdog': 'watchdog'
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ],
      
      )
