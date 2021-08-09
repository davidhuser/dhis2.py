#!/usr/bin/env python

import os
import sys
from codecs import open
from shutil import rmtree

from setuptools import setup, find_packages, Command

here = os.path.abspath(os.path.dirname(__file__))

requirements = ["requests>=2.24.0,<3.0", "logzero>=1.5.0", "Pygments>=2.7.1"]


about = {}
with open(os.path.join(here, "dhis2", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open("README.rst", "r", "utf-8") as f:
    readme = f.read()


class PublishCommand(Command):
    """Support setup.py publish."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds...")
            rmtree(os.path.join(here, "dist"))
        except (OSError, IOError):
            pass

        self.status("Building Source and Wheel (universal) distribution...")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine...")
        os.system("twine upload dist/*")

        self.status("Pushing git tags...")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    keywords="dhis2",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.6",
    install_requires=requirements,
    license=about["__license__"],
    zip_safe=False,
    classifiers=(  # https://pypi.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ),
    cmdclass={"publish": PublishCommand},
)
