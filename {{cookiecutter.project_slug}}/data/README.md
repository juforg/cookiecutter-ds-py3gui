# {{ cookiecutter.project_name }} - Data

Here you can find all category data files.

Strict regulations：

do not use uncompressed file.

eg:

df.to_csv('data/0_raw/data.csv.gz', compression='gzip', index=False)
df.to_csv('data/0_raw/data.csv.zip', compression='zip', index=False)

df = pd.read_csv('data/0_raw/data.csv.gz')
df = pd.read_csv('data/0_raw/data.csv.zip')
