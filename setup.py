from setuptools import setup, find_packages, find_namespace_packages

with open("README.md", "r") as f:
    readme = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().split("\n")

setup(
    name='cinnabar',
    version='0.1.0',
    author='Hanshi Sun',
    author_email='hanshi.sun@outlook.com',
    description='Efficiently monitor GPU resources and schedule tasks for optimal performance.',
    license='GNU',
    packages=find_packages(
        include=(
            'cinnabar_server',
        )
    ),
    package_dir={
        'cinnabar_server': 'cinnabar_server',
    },
    package_data={
        "cinnabar_server": ["static/**", "templates/**"],
        "misc":["README.md", "requirements.txt", "setup.py"]
    },
    install_requires=requirements,
    long_description=readme,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'cinnabar = main:main',
        ],
    },
)
