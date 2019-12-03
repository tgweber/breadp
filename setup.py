from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='breadp',
    version='0.0.1',
    descripion='Benchmarks for REseArch Data Products',
    long_description=readme,
    author='Tobias Weber',
    author_email='mail@tgweber.de',
    url='https://github.com/tgweber/breadp',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
