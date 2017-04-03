from setuptools import setup,find_packages

setup(
  name = 'recast-backend',
  version = '0.0.1',
  packages = find_packages(),
  entry_points= {
        'console_scripts': [
           'recast-directsub  = recastbackend.submitcli:submit',
           'recast-listen     = recastbackend.listener:listen',
           'recast-track      = recastbackend.tracker:track',
           'recast-status      = recastbackend.statuscli:status',
         ]
},
  include_package_data = True,
  install_requires = [
    'Click',
    'recast-api',
    'requests',
    'glob2'
  ],
  dependency_links = [
    'https://github.com/lukasheinrich/socket.io-python-emitter/tarball/master#egg=socket.io-emitter-0.0.1',
    'https://github.com/recast-hep/recast-api/tarball/master#egg=recast-api-0.0.1',
    'https://github.com/recast-hep/recast-celery/tarball/master#egg=recast-celery-0.0.1'
  ]
)
