Quick Start Guide
=================

#Getting the code
1. Clone the git repo
2. Install a virtual env and get all requirements
    ```
    cd <the-shortest-url-repo-root>
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements/requirements.txt
    ```
3. Run Unit tests
    ```
    cd <the-shortest-url-repo-root>
    python3 setup.py test
    ```
#Starting the app
You can run this application using docker or as a python process.
## Run with Docker
1. Build docker image
    ```
    cd <the-shortest-url-repo-root>
    docker build -t shortlink:latest .
    ```
2. Run docker container to start the server
    ```
    docker run --publish 5000:5000 shortlink
    ```
## Run without Docker
1. Make sure you are inside the venv
    ```
    cd <the-shortest-url-repo-root>
    source venv/bin/activate
    ```
2. Run the flask app
    ```
    cd <the-shortest-url-repo-root>/shortlink
    flask run
    ```
# Using the APIs
1. Find the API documentation at http://localhost:5000/
2. You can try out the APIs here itself via swagger UI
3. Or try them out with curl
    ```
    curl http://localhost:5000/shortlink/encode \
    -d '{"long_url": "https://loooonngg.somewhere/something"}' \
    -H 'Content-Type:application/json'
    ```
    ```
    curl http://localhost:5000/shortlink/decode/short.est/qW8Cpd \
    -H 'Content-Type:application/json'
    ```
# Running API functional tests
1. Install test requirements
    ```
    cd <the-shortest-url-repo-root>/
    pip install -r requirements/test.txt
    ```
2. Start the server if not running
    ```
    cd <the-shortest-url-repo-root>/shortlink
    flask run
    ```
3. Run tests
    ```
   cd <the-shortest-url-repo-root>/api_tests
   pytest
   ```
