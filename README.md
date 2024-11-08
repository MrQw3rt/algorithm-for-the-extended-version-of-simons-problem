# Algorithm for Extended Version of Simon's Problem

## Setup

### Using a Virtual Environment (Recommended)

In the project root, run
```
$ python3 -m venv .venv
$ source .venv/bin/activate
```
To install the necessary packages, run
```
(.venv) $ pip3 install -r requirements.txt
```
You can always exit the virtual environment with 
```
$ deactivate
```

### Using global Environment (Not Recommended)

Simply run
```
$ pip3 install -r requirements.txt
```
Note that the above command installs `qiskit` and `qiskit-aer` system-wide!


## Run Test Suite

In the project root, run
```
$ python3 -m unittest discover -v -s ./test
```
