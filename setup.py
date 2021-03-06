from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='breadp',
    version='0.0.15',
    description='Benchmarks for REseArch Data Products',
    long_description=readme,
    author='Tobias Weber',
    author_email='mail@tgweber.de',
    url='https://github.com/tgweber/breadp',
    license=license,
    package_data = {
        "breadp": ["checks/resources/*.json", "checks/resources/*.csv"]
    },
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=["rdp @ git+https://github.com/tgweber/rdp",
                      "langdetect @ git+https://github.com/Mimino666/langdetect",
                      "pandas",
                      "requests"]

)
