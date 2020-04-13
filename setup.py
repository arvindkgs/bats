from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="basic-acceptance-test-suite",
    version="0.0.1",
    author="Arvind Kumar GS",
    author_email="arvind.kumar.gs@oracle.com",
    description="This tool can be used to retrive and check properties defined in multiple files (local or remote).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages('src'),
	package_dir={'':'src'},
    include_package_data=True,
    install_requires=['apacheconfig', 'decorator', 'ply', 'argparse', 'pbr', 'six', 'jsonpath-rw', 'jsonpath-rw-ext', 'setuptools'],
    classifiers=[
        "Programming Language :: Python :: 2.6"
    ],
)
