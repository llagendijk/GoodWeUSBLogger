import os
from setuptools import setup, find_packages
import codecs


def read(fname):
    with codecs.open(os.path.join(__file__), 'r') as fp:
        return fp.read()


def set_data_files():
    data_files = [('/usr/lib/systemd/system/', ['goodweusb2mqtt.service'])]
    if not os.path.isfile('/etc/goodwe.conf'):
        data_files.append(('/etc/', ['goodwe.conf']))
    return data_files


setup(
    name='goodweusb2mqtt',
    version='1.0',
    packages=find_packages(),
    scripts=['goodweusb2mqtt'],
    package_data={
        '': ['*.md'],
    },
    include_package_data=True,
    data_files=set_data_files(),
    py_modules=['GoodWeCommunicator', 'hidrawpure', 'Inverter2Domo'],
    description='Goodwe USB inverter to MQTT server',
    license='GPLv3+',
    long_description=read("README.md"),
    author= 'Louis Lagendijk based on version by Arjen (sircuri): Arjen <arjen@vanefferenonline.nl>',
    author_email='louis.lagendijk@gmail.com',
    install_requires=['configparser', 'paho-mqtt', 'simplejson', 'ioctl_opt', 'pyudev'],
    classifiers=[
        "Environment :: No Input/Output (Daemon)",
        "Development Status :: 4 - Beta", "License :: OSI Approved :: "
    ])
