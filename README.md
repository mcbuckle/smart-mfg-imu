# Running
In the future, there will be a dockerfile to make setup easier.
For now, you must do the following:

1. Create a python virtual environment (optional but recommended)
    a. `python3 -m venv .venv`
    b. `source .venv/bin/activate`
2. Install dependencies
    a. `pip install -r requirements.txt`
3. Run `src/main.py`
    a. `python src/main.py`
    b. Run `python src/main.py -u` to see real-time data being collected

# TODO:
1. Create "fake" IMU class for testing on devices without an IMU connection
    a. Just opens a sample data csv and reads the data from there.
       When it reaches the end, loop back to the beginning
       Wrap imports in the init file in a try catch block
2. Rename `src/` folder to `imu` or something
    a. Rename `src/main.py` to `src/__init__.py` so it is a module

## NTP stuff
Query NTP server on start to set device's time. ***Not*** every time we get a data point
