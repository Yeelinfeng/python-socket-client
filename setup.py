from setuptools import setup, find_packages

setup(
    name="python-socket-client",
    version="1.0.0",
    description="A reusable TCP/UDP socket client library with reconnection and timeout support",
    author="Your Name",
    license="MIT",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
