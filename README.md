# Smart Object Library

* A library of 'smart' objects for BIM (Building Information Modelling) purposes

* This repo essentially contains the backend API and data engine for smart object library frontends

### Dependencies

* You will need to have the following installed:
    * Docker
    * Conda (with Python 3.12+) 


## Installation
* Clone the repo and navigate to the root directory
* _Ensure_ that Docker is installed and running

* If Conda isn't already initialized on your machine, enter (then restart your terminal):

```bash
conda init
```

* Create a conda env with:

```bash
conda env create -f environment.yml # Don't forget to add 'env'
```

* Activate the environment with:

```bash
conda activate SmartObjectLibrary
```

* Then run:

```bash
python main.py
```