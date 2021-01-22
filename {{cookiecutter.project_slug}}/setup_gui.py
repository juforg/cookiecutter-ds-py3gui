import sys

from setuptools import find_packages, setup
import versioneer
import os
from cx_Freeze import setup, Executable

# get current directory
path = os.path.realpath(os.path.abspath(__file__))
current_directory = os.path.dirname(path)


build_exe_options = {'packages': ['{{cookiecutter.repo_name}}'], 'excludes': ['numpy'], 'includes': ["tkinter"]}
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name='{{ cookiecutter.pkg_name }}',
      version=versioneer.get_version(),
      description='{{cookiecutter.short_description}}',
      options={'build_exe': build_exe_options},
      executables=[Executable('{{cookiecutter.repo_name}}/__main__.py', base=base, target_name='{{cookiecutter.pkg_name}}')])
