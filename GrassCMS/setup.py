#!/usr/bin/env python
# For some reason, building exes with py2exe doesnt work right now.
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import os

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

data_files = []

for dirpath, dirnames, filenames in os.walk('grasscms'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(name='GrassCMS',
      version='0.0.1',
      description='GrassCMS',
      url='http://www.grasscms.com/',
      download_url='http://www.grasscms.com',
      license='GPL2',
      requires=['sqlalchemy' ],
      classifiers=[
          'Development Status :: 4 - Beta',
      ],
      long_description="GrassCMS, easy-to-use content management system",
      packages=['grasscms'],
      data_files=data_files,
      package_data={
        'grasscms' : [
            'static/'
            'templates/'
            ]
      },
      entry_points="""
        [console_scripts]
        grasscms = grasscms.server:server
      """
     )
