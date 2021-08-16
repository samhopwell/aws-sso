import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(
    name="aws-sso",
    version="1.0.0",
    author="Sam Hopwell",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samhopwell/aws-sso",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
