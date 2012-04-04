import os
from setuptools import setup, find_packages


VERSION = "0.1"

setup(
    name = "fm.utils",
    version = VERSION,
    author="Julian Bez",
    author_email="julian@freshmilk.tv",
    url="http://www.freshmilk.tv",
    description = """Freshmilk Utils App""",
    packages=find_packages(),
    namespace_packages = ['fm'],
    include_package_data = True,
    zip_safe=False,
    license="None",
    install_requires = ["requests"]
)
