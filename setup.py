from setuptools import setup, find_packages
# Import parse_requirements:
# https://stackoverflow.com/a/49867265/4527337
try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements

# Parse the requirements from requirements.txt
requirements = list(parse_requirements('requirements.txt', session=False))

# Convert the parsed requirements into a list of strings
try:
    install_requires = [str(req.req) for req in requirements]
except AttributeError:
    install_requires = [str(req.requirement) for req in requirements]

setup(
    name="watcloud-utils",
    version="0.0.1",
    description="Utility package for WATcloud",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/watonomous/watcloud-utils",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
)
