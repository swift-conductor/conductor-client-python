import os
import setuptools

setuptools.setup(version=os.getenv('CONDUCTOR_PYTHON_VERSION') or '0.1.0')
