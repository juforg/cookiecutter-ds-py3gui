from setuptools import find_packages, setup
import versioneer

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
    url='',
    description='{{ cookiecutter.short_description }}',
    author='{{ cookiecutter.author_name }}',
    author_email='{{ cookiecutter.email }}',
    license='{% if cookiecutter.open_source_license == 'MIT License' %}MIT{% elif cookiecutter.open_source_license == 'BSD License' %}BSD-3{% endif %}',
    install_requires=[
                        'attrs'
                        , 'numpy'
                        , 'versioneer'
                        , 'click'
                        ]
)
