import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webmontage",
    version="1.0.0",
    author="Dylan Williams",
    author_email="dylan@dylanfw.com",
    description="Web page montage generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dylanfw/webmontage",
    install_requires=["gitpython>=2", "selenium", "opencv-python"],
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["webmontage = webmontage.command:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
