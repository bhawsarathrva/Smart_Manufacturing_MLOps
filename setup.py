from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="SMART_MANUFACTURING",
    version="0.1",
    author="Atharv",
    packages=find_packages(),
    install_requires = requirements,
)