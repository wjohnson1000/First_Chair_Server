from distutils.core import setup
setup(name='firstchair',
      version='1.0',
      package_dir = {'modules': 'process/modules'}
      packages=['modules'],
      py_modules=['process.modules'],
      )
