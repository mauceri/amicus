#!/usr/bin/env python3
import os

from setuptools import find_packages, setup

def exec_file(path_segments):
    """Execute a single python file to get the variables defined in it"""
    result = {}
    code = read_file(path_segments)
    exec(code, result)
    return result


def read_file(path_segments):
    """Read a file from the package. Takes a list of strings to join to
    make the path"""
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *path_segments)
    with open(file_path) as f:
        return f.read()


long_description = read_file(("README.md",))


setup(
    name="test",
    version='0.1.0',
    url="https://github.com/mauceri/amicus",
    description="Un assistant qui vous veut du bien",
    packages=find_packages(),
    install_requires=[
        "matrix-nio",
        "amicus_interfaces",
        "semaphore-bot==v0.16.0",
        "dspy-ai",
        "requests",
        "transformers",
        "sentencepiece",
        "protobuf",
        "jinja2",
        "openai",
        "langchain",
        "langchainhub"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],


)