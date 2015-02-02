from distutils.core import setup

setup(
    name="acontrol",
    version="1.0",
    packages=['acontrol'],
    scripts=['bin/acontrol'],
    description="AARTFAAC Control System",
    long_description=open('README.rst').read(),
    url="http://github.com/aartfaac/control",
    author="John Swinbank",
    author_email="swinbank@aartfaac.org",
    maintainer="Folkert Huizinga",
    maintainer_email="f.huizinga@uva.nl", 
    requires=['twisted']
)
