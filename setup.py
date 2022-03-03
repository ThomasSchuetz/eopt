from setuptools import setup

setup(
    name="energy_system_optimizer",
    version="1.0",
    description="Example on how to build a modular energy system optimizer",
    author="TS",
    author_email="foomail@foo.com",
    packages=["energy_system_optimizer"],  # same as name
    install_requires=["ortools"],  # external packages as dependencies
)
