from setuptools import find_packages, setup
import versioneer

setup(
    name='{{ cookiecutter.package_name }}',
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        'console_scripts': [
            '{{ cookiecutter.package_name }} = {{ cookiecutter.package_name }}.__main__:main'
        ]
    },
    url='{{ cookiecutter.url }}',
    description='{{ cookiecutter.description }}',
    author='{{ cookiecutter.author_name }}',
    author_email='{{ cookiecutter.email }}',
    license='{% if cookiecutter.open_source_license == 'MIT' %}MIT{% elif cookiecutter.open_source_license == 'BSD-3-Clause' %}BSD-3{% endif %}',
    install_requires=[
                        'attrs'
                        , 'numpy'
                        , 'versioneer'
                        {% if cookiecutter.cli_tool == "docopt" %}, 'docopt'{% elif cookiecutter.cli_tool == "click" %}, 'click'{% endif %}
                        ]
)
