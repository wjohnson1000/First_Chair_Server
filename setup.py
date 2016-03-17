from distutils.core import setup
setup(name='firstchair',
      version='1.0',
      packages=['modules'],
      package_dir = {'modules': 'process/modules'}
      py_modules=['process.modules'],
     )
