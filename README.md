# README

## How to build and run

First, ensure both .venv and Python 3.9 or higher are installed. Now, navigate to the project root directory (the folder with the toml and run.py), and run these commands: 

### Windows

Ensure both the Python Launcher, Pip, and .venv are installed. 

```
py -3.13 -m venv .venv --clear && ^
.venv\Scripts\activate
```

Now run `pip install -e .` or `pip install -e .` if you want debug information. 

Now you can run the project with `python run.py`

### Linux

Ensure both Pip and Python are installed.

```
python3.13 -m venv --clear .venv && \
source .venv/bin/activate
```



Now run `pip install -e .` or `pip install -e .` if you want debug information.

Now you can run the project with `python run.py`










