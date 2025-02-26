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
* Create a conda env with:

```bash
conda create -f environment.yml
```

* Activate the environment with:

```bash
conda activate SmartObjectLibrary
```

* Then run:

```bash
python main.py
```