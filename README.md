# Smart Object Library

* A library of 'smart' objects for BIM (Building Information Modelling) purposes

* This repo essentially contains the backend API and data engine for smart object library frontends

## Running the API
* Clone the repo and navigate to the root directory
* Ensure you have Docker installed and running on your machine

* Build the image:
```bash
docker build -t pl-api .
```

* Then run the container:
```bash 
docker run -d -p 5000:5000 pl-api
```

* The API should now be accessible at `http://localhost:5000`