from setuptools import setup, find_packages
setup(
    name="pyflotilla",
    version="0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=['pyserial>=3'],
    author="Itxaka Serrano Garcia",
    author_email="itxakaserrano@gmail.com",
    description="Python library to interact with flotilla modules",
    license="Apache",
    keywords="flotilla",
)
