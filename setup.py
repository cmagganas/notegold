from setuptools import setup, find_packages

setup(
    name="notegold",
    version="0.1.0",
    description="Transform meeting notes into valuable content assets",
    author="Christos Magganas",
    author_email="example@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "notegold=src.main:main",
        ],
    },
    python_requires=">=3.8",
) 