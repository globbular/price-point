import setuptools


with open("README.md",encoding="utf8") as fp:
    long_description = fp.read()


setuptools.setup(
    name="price_point",
    version="0.0.1",

    description="An automatic price checker!",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "price_point"},
    packages=setuptools.find_packages(where="price_point"),

    install_requires=[
        "aws-cdk.core",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
