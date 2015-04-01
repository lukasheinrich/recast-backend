from setuptools import setup,find_packages

setup(
  name = 'recast-backend',
  version = '0.0.1',
  packages = find_packages(),
  entry_points={
        'console_scripts': ['recast-prodsub = recastbackend.submitcli:submit']
      },
  install_requires = [
    'Celery',
    'Click',
    'redis'
  ]
)
