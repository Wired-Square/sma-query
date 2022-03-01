import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sma_query_sw",
    version="0.0.3",
    author="Garth Berry",
    author_email="garth@wiredsquare.com",
    description="SMA Sunny Boy Inverter Query Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wired-square/sma-query",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
