import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

with open("version", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="redis-property",
    version=version,
    author="Ed__xu__Ed",
    author_email="m.tofu@qq.com",
    description="A decorator for caching properties in Redis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ed-XCF/redis-property",
    py_modules=["redis_property"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=install_requires,
    include_package_data=True,
)
