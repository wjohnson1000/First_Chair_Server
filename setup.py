from distutils.core import setup
setup(name='firstchair',
      version='1.0',
      packages=['pkg'],
      package_dir={'pkg': './'},
      py_modules=['process.processconfig', 'db.db_config']
      )
