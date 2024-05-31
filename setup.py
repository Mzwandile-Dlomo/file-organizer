# define the package and entry point
from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as req:
        return req.read().splitlines()

setup(
    name='file-organizer',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'file-organizer=file-organizer.organizer:main',
        ],
    },
    package_data={
        'file-organizer': ['rules.json'],
    },
    author='Mzwandile Dlomo',
    author_email='world.mjdlomo@gmail.com',
    description='A terminal-based file organizer',
    url='https://github.com/Mzwandile-Dlomo/file-organizer',
    license='MIT',
)
