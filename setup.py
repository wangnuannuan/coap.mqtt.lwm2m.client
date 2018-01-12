#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup

setup(
    name="wcli",
    version="1.0.0",
    description="client command line tool for test",
    author="Nuannuan Wang",
    author_email="1961295051@qq.com",
    packages=["wcli"],
    entry_points={
    'console_scripts': [
    'coap-client=wcli.c_coap:sync_main',
    'mqtt-client=wcli.c_mqtt:main',
    'lwm2m-client=wcli.c_lwm2m:main'
    ]
    },
)
