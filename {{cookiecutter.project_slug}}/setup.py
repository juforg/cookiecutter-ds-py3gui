from setuptools import find_packages, setup
import versioneer
import os

# get current directory
path = os.path.realpath(os.path.abspath(__file__))
current_directory = os.path.dirname(path)

# get version
# version = {}
# with open(f"{current_directory}/{{cookiecutter.repo_name}}/_version.py") as f:
#     exec(f.read(), version)  # then we can use it as: version['__version__']

# get long description from readme
with open(f"{current_directory}/README.md", "r") as fh:
    long_description = fh.read()

try:
    with open(f"{current_directory}/requirements.txt", "r") as fh:
        requirements = fh.readlines()
except:
    requirements = ['PySimpleGUI>=4.18', 'pyperclip', 'plyer', 'certifi', 'pycurl', 'pillow', 'pystray']

setup(
    name='{{ cookiecutter.pkg_name }}',
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        'console_scripts': [
            '{{ cookiecutter.pkg_name }} = {{ cookiecutter.pkg_name }}.__main__:main'
        ]
    },
    description='{{ cookiecutter.short_description }}',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    author='{{ cookiecutter.author_name }}',
    author_email='{{ cookiecutter.email }}',
    keywords="",
    project_urls={
        'Source': ' ',
        'Tracker': '',
        'Releases': '',
        'Screenshots': ''
    },
    license='{% if cookiecutter.open_source_license == 'MIT License' %}MIT{% elif cookiecutter.open_source_license == 'BSD License' %}BSD-3{% endif %}',
    install_requires=requirements,
    python_requires='>=3.7',

)
