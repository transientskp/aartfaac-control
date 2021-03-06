from distutils.core import setup
import sys
import acontrol, aclient

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="AControl",
    description='Aartfaac control system - daemon that boots aartfaac observations',
    author='Folkert Huizinga',
    author_email='f.huizinga@uva.nl',
    version='1.0',
    url='https://github.com/transientskp/aartfaac-control',
    packages=[
        'acontrol',
        'acontrol.test',
        'aclient',
        'twisted'
    ],
    scripts=[],
    package_data={
        'twisted': ['plugins/acontrol_plugin.py', 'plugins/aclient_plugin.py']
    },
    install_requires=required
)
