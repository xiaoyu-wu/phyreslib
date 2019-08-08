import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phyreslib",
    version="0.0.0.dev",
    author="Xiaoyu Wu",
    author_email="xywu@utexas.edu",
    description="A package for physics research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaoyu-wu/phyreslib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)