from distutils.core import setup
import sys
import acontrol, aclient

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="AControl",
    description='Aartfaac control system - starts the pipelines during a valid observation',
    author='Folkert Huizinga',
    author_email='f.huizinga@uva.nl',
    version='1.0',
    url='https://github.com/transientskp/aartfaac-control',
    packages=[
        'acontrol',
        'aclient',
        'twisted'
    ],
    scripts=[],
    package_data={
        'twisted': ['plugins/acontrol_plugin.py', 'plugins/aclient_plugin.py']
    },
    install_requires=required
)
