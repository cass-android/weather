from setuptools import setup

setup(
    name='weather',
    packages=['weather'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
