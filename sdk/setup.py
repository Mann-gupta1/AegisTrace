from setuptools import setup, find_packages

setup(
    name="aegistrace",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.28.0",
    ],
    python_requires=">=3.10",
    description="Trace SDK for AegisTrace Agent Observability Platform",
    author="AegisTrace",
)
