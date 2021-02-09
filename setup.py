import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="solax",
    use_scm_version=True,
    author="Robin Wohlers-Reichel",
    author_email="me@robinwr.com",
    description="Solax inverter API client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/squishykid/solax",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'aiohttp>=3.5.4',
        'voluptuous>=0.11.5'
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
