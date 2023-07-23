from setuptools import find_packages, setup

setup(
    name='icbc',
    packages=find_packages(include=['icbc.road_test']),
    version='0.0.1',
    description='ICBC API helper library.',
    author='Elio Capelati Jr',
    setup_requires=['requests==2.31.0'],
    tests_require=['pytest==7.4.0', 'pytest-runner==6.0.0'],
    license='MIT',
)
