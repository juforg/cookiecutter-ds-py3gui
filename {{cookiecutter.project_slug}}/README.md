{{cookiecutter.project_name}}
==============================

{{cookiecutter.short_description}}

## Installation

    pip install -U pipenv  # if you haven't already
    pipenv install
    pipenv run python app.py
    
## Development

    pipenv install --dev
    pipenv shell
    
## Test

    pytest


## Directory structure
------------
{% if cookiecutter.open_source_license != "Not open source" -%}
    ├── LICENSE                   <- Your project's license.
{%- endif %}
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── 0_raw                 <- The original, immutable data dump.
    │   ├── 1_external            <- Data from third party sources.
    │   ├── 2_interim             <- Intermediate data that has been transformed.
    │   └── 3_processed               <- The processed, pureness data sets for modeling.
{% if cookiecutter.use_docker == "Yes" -%}
    ├── docker               <- docker files
{%- endif %}
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
{%- if cookiecutter.use_gui == "Y" %}
    |   ├── {{cookiecutter.repo_name}}_gui_main.py           <- Script with option for running the final analysis.
{%- endif %}
{%- if cookiecutter.workflow_automation == "Python" %}
    |   ├── {{cookiecutter.repo_name}}_main.py               <- Script with option for running the final analysis.
{%- elif cookiecutter.workflow_automation == "Snakemake" %}
    |   ├── Snakefile                <- Script with options for running the final analysis.
{%- elif cookiecutter.workflow_automation == "Make" %}
    |   ├── Makefile           <- Makefile with commands like `make data` or `make train` Script with options for running the final analysis.
{%- endif %}
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io
{%- elif cookiecutter.package_manager == "pipenv" %}
    ├── Pipfile                   <- The Pipfile for reproducing the analysis environment
{%- endif %}
    ├── .gitignore                <- GitHub's excellent Python .gitignore customized for this project


--------

|包名|说明|版本要求|
|----|----|----|
|python-dotenv|加载.flaskenv配置到环境变量中||
|mip|混合整数规划|1.9.0|
|PuLP|混合整数规划|2.0|
|celery|异步任务/定时任务框架|4.3|
|flask-redis|redis集成|可被当作分布式锁|
|marshmallow|序列化反序列化包|3|
|pandas|结构化数据的分析工具集||
|sqlacodegen|生成sqlalchemy的model代码||
|cachetools|方法结果缓存||
|pyarmor|python代码加密||
|aiohttp|异步http请求||
|pick|命令行选则器||
|click|命令行强化(不选用argparse、docopt、fire)|7.0|
|joblib|模型转文件||
|pathlib2|替换os.path|
|pygubu|GUI布局工具|
|pystray|系统托盘|
|plyer|系统托盘提示|

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

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
[pygubu]: https://github.com/alejandroautalan/pygubu