from setuptools import setup, find_packages
from games.version import get_version


def get_install_requirements(filename):
    requirements = []
    with open(filename) as f:
        for line in f:
            if line.strip().startswith('-'):
                continue
            requirements.append(line)
    return requirements


install_requirements = get_install_requirements('requirements.txt')

test_requires = [
    'pytest',
    'pytest-django',
    'pytest-cov',
]

setup_requires = [
    'pytest-runner',
]

setup(
    name='games',
    version=get_version(),
    packages=find_packages(exclude=['tests']),
    install_requires=install_requirements,
    license='CUSTOM',
    author='dev-python development group',
    author_email='python-development@nic.ru',
    description='games',
    tests_require=test_requires,
    extras_require={'test': test_requires},
    setup_requires=setup_requires,
    include_package_data=True,
)
