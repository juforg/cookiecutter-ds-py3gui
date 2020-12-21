# Cookiecutter Data Science Py3Tkinter Template
![Python version](https://img.shields.io/badge/Python-3.x-informational)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

_A logical, reasonably standardized, but flexible project structure for doing and sharing data science work._
A template for command-line utility **cookiecutters** to create a Python 3 package with a Tkinter UI.
`cookiecutter` is a command-line utility that creates projects from 
cookiecutters (project templates). See
[cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io/en/1.7.0/index.html).

#### [Project homepage](http://drivendata.github.io/cookiecutter-data-science/)

## Motivation

A project template that promotes good practices for reproducible 
data science (immutablity of raw data, seperation of exploratory code and 
"final" analysis code), while giving options for more or less complex projects

### Features
-----------

* Works on 3.5 (Earlier Python versions untested).
* JSON switches to configure GUI components
    * Navigation bar
    * Status bar
    * Tool bar
* Organized in classes per stack over flow response:  http://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
* [Pipenv] for managing packages and virtualenvs in a modern way.
* [Prefect] for modern pipelines and data workflow.
* [Weights and Biases] for experiment tracking.
* [FastAPI] for self-documenting fast HTTP APIs - on par with NodeJS and Go - based on [asyncio], [ASGI], and [uvicorn].
* Modern CLI with [Typer].
* Batteries included: [Pandas], [numpy], [scipy], [seaborn], and [jupyterlab] already installed.
* Consistent code quality: [black], [isort], [autoflake], and [pylint] already installed.
* [Pytest] for testing.
* [GitHub Pages] for the public website.

### Requirements to use the cookiecutter template:
-----------
 - Python 3.5+
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
```bash
    cookiecutter https://github.com/drivendata/cookiecutter-data-science
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
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── 0_raw                 <- The original, immutable data dump.
│   ├── 0_external            <- Data from third party sources.
│   ├── 1_interim             <- Intermediate data that has been transformed.
│   └── 2_final               <- The final, canonical data sets for modeling.
│
├── docs               <- A default Sphinx project; see sphinx-doc.org for details
│   ├── data_dictionaries     <- Data dictionaries
│   └── references            <- Papers, manuals, and all other explanatory materials.
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `01_cp_exploratory_data_analysis.ipynb`.
│
├── output
│   ├── features              <- Fitted and serialized features
│   ├── models                <- Trained and serialized models, model predictions, or model summaries
│   └── reports               <- Generated analyses as HTML, PDF, LaTeX, etc.
│       └── figures           <- Generated graphics and figures to be used in reporting

├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   │
│   ├── data           <- Scripts to download or generate data
│   │   └── make_dataset.py
│   │
│   ├── features       <- Scripts to turn raw data into features for modeling
│   │   └── build_features.py
│   │
│   ├── models         <- Scripts to train models and then use trained models to make
│   │   │                 predictions
│   │   ├── predict_model.py
│   │   └── train_model.py
│   │
│   └── visualization  <- Scripts to create exploratory and results oriented visualizations
│       └── visualize.py
│
└── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io
├── Pipfile                   <- The Pipfile for reproducing the analysis environment
```

## Contributing

We welcome contributions! [See the docs for guidelines](https://drivendata.github.io/cookiecutter-data-science/#contributing).

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