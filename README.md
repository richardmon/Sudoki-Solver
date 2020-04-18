# 🤖 Sudoku Solver

## What are you looking at?
This is a simple web application that solves a sudoku by simply taking a picture (*ideally*).

The entire application stack is build around the python ecosystem, using just a little bit of javascript and css for the UI.


## ⚠️Warning
The neural network to detect the numbers is a simple MLP (multilayer perceptron) which are not known to be very accurate
with image recognition, so manual editing is needed.

## Build and Execution
In order to install all the necessary dependencies type *pip install -r requirements.txt*, this will install all the libraries needed.
For ease of use docker is also needed to run the redis database.

* Run redis docker container by typing ```docker run --name redis -d redis -p 6379:6379``` in the terminal
* Set URL_REDIS to localhost by typing ``` export URL_REDIS=127.0.0.1 ```
* Install all the python libraries required for the project ``` pip install -r requirements.txt ```
* To start the web server type ``` FLASK_APP=server.app python -m flask run ```
* Start the worker by typing ``` rq worker ```



## Common Issues
* ***Pip install, not enough space***
If there is still space in the harddrive create a new temp dir by typing ``` mkdir ~/tmp/ ```
and create the global variable ``` export TMPDIR=~/tmp ```, and then try again.
