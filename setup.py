from setuptools import setup,find_packages

setup(
  name = 'recast-backend',
  version = '0.0.1',
  packages = find_packages(),
  entry_points={
        'console_scripts': [
           'recast-prodsub = recastbackend.submitcli:submit',
           'recast-listen  = recastbackend.listener:listen'
         ]
      },
  include_package_data = True,
  install_requires = [
    'Celery',
    'Click',
    'redis',
    'socket.io-emitter',
  ],
  dependency_links = [
    'https://github.com/ziyasal/socket.io-python-emitter/tarball/master#egg=socket.io-emitter-0.1.3'
  ]
)
