try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNUtilities",
    version="3.0.0",
    description="Utility classes and functions for SpiNNaker projects",
    url="https://github.com/SpiNNakerManchester/SpiNNUtilities",
    license="GNU GPLv3.0",
    packages=['spinn_utilities'],
    install_requires=[]
)
