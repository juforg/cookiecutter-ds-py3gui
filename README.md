# Cookiecutter Data Science Py3Tkinter Template
<p align="center">
<a href="https://github.com/juforg/cookiecutter-ds-py3gui/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/juforg/cookiecutter-ds-py3gui?style=social"></a>
    <a>
        <img src="https://img.shields.io/badge/Python-3.x-informational" />
    </a>
    <a href="https://github.com/juforg/cookiecutter-ds-py3gui/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/juforg/cookiecutter-ds-py3gui?color=blue"></a>
</p>


- A logical, reasonably standardized, but flexible project structure for doing and sharing data science work._
- A template for command-line utility **cookiecutters** to create a Python 3 package with a PySimpleGUI.
- `cookiecutter` is a command-line utility that creates projects from 
cookiecutters (project templates). See
[cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io/en/1.7.0/index.html).

#### [Project homepage](https://github.com/juforg/cookiecutter-ds-py3gui/)

## Motivation

A project template that promotes good practices for reproducible 
data science (immutablity of raw data, seperation of exploratory code and 
"final" analysis code), while giving options for more or less complex projects

### Features
-----------

* Works on 3.7 (Earlier Python versions untested).
* choice for managing packages and virtualenvs
    - [Pipenv] 
    - pip
    - conda
* Modern CLI with [Typer].
* Batteries included: [Pandas], [numpy], [scipy], [seaborn], and [jupyterlab] already installed.
* Consistent code quality: [black], [isort], [autoflake], and [pylint] already installed.
* [Pytest] for testing.

### Requirements to use the cookiecutter template:
-----------
 - Python 3.7+
 - [Cookiecutter Python package](http://cookiecutter.readthedocs.org/en/latest/installation.html) >= 1.4.0: This can be installed with pip by or conda depending on how you manage your Python packages:

Install the latest Cookiecutter and Pipenv:
``` bash
$ pip install -U pipenv cookiecutter
```

or

``` bash
$ conda config --add channels conda-forge
$ conda install cookiecutter
```

### To start a new project, run:
------------
[![asciicast](https://asciinema.org/a/uyfETRhchKNX0FyQiuB2ZX3IY.svg)](https://asciinema.org/a/uyfETRhchKNX0FyQiuB2ZX3IY)
```bash
    cookiecutter gh:juforg/cookiecutter-ds-py3gui
```

Get inside the project:

    cd <repo_name>
    pipenv shell  # activates virtualenv

[![asciicast](https://asciinema.org/a/244658.svg)](https://asciinema.org/a/244658)


### The resulting directory structure
------------

The directory structure of your new project looks like this: 

```
├── LICENSE      <- Your project's license.
   ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── 0_raw                 <- The original, immutable data dump.
    │   ├── 1_external            <- Data from third party sources.
    │   ├── 2_interim             <- Intermediate data that has been transformed.
    │   └── 3_processed               <- The processed, pureness data sets for modeling.
    ├── docker               <- docker files
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │   ├── data_dictionaries     <- Data dictionaries
    |   └── references            <- Papers, manuals, and all other explanatory materials.
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `01_sj_exploratory_data_analysis.ipynb`.
    ├── output
    │   ├── features              <- Fitted and serialized features
    │   ├── models                <- Trained and serialized models, model predictions, or model summaries
    │   └── reports               <- Generated analyses as HTML, PDF, LaTeX, etc.
    │       └── figures           <- Generated graphics and figures to be used in reporting
    │
    ├── tests              <- test scripts
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── {{cookiecutter.repo_name}}                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data or etl
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   ├── gui       <-  Scripts to support interactive with GUI
    │   │   └── locale      <-  I18N
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   |   └── visualize.py
    |   ├── {{cookiecutter.repo_name}}_gui_main.py           <- Script with option for running the final analysis.
    |   ├── {{cookiecutter.repo_name}}_main.py               <- Script with option for running the final analysis.
    |   ├── Snakefile                <- Script with options for running the final analysis.
    |   ├── Makefile           <- Makefile with commands like `make data` or `make train` Script with options for running the final analysis.
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io
    ├── Pipfile                   <- The Pipfile for reproducing the analysis environment
    ├── .gitignore                <- GitHub's excellent Python .gitignore customized for this project
```


### Installing development requirements
------------

    pip install -r requirements.txt

### Running the tests
------------

    py.test tests


### screenshot
----------

This project is meant to adapt (and borrows liberally from) Driven Data's 
[cookicutter-data-science](https://drivendata.github.io/cookiecutter-data-science#keep-secrets-and-configuration-out-of-version-control) 
structure and philosophy to slightly different needs.

## References
- https://github.com/drivendata/cookiecutter-data-science
- https://github.com/crmne/cookiecutter-modern-datascience
- https://github.com/gvoysey/cookiecutter-python-scientific
- https://github.com/Jswig/cookiecutter-flexible-ml
- https://github.com/docker-science/cookiecutter-docker-science
- https://github.com/PySimpleGUI/PySimpleGUI
- https://github.com/tirthajyoti/DS-with-PySimpleGUI
- [cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.0/min) >= 1.1


[Cookiecutter]: https://github.com/audreyr/cookiecutter
[Pipenv]: https://pipenv.pypa.io/en/latest/
[Weights and Biases]: https://www.wandb.com/
[MLFlow]: https://mlflow.org/
[asyncio]: https://docs.python.org/3/library/asyncio.html
[Typer]: https://typer.tiangolo.com/
[Pandas]: https://pandas.pydata.org/
[numpy]: https://numpy.org/
[scipy]: https://www.scipy.org/
[seaborn]: https://seaborn.pydata.org/
[jupyterlab]: https://jupyterlab.readthedocs.io/en/stable/
[black]: https://github.com/psf/black
[isort]: https://github.com/timothycrosley/isort
[autoflake]: https://github.com/myint/autoflake
[pylint]: https://www.pylint.org/
[Pytest]: https://docs.pytest.org/en/latest/
[PySimpleGUI]: https://github.com/PySimpleGUI/PySimpleGUI