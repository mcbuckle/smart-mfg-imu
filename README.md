# Running
In the future, there will be a dockerfile to make setup easier.
For now, you must do the following:

1. Create a python virtual environment (optional but recommended)
    a. `python3 -m venv .venv`
    b. `source .venv/bin/activate`
2. Install dependencies
    a. `pip install -r requirements.txt`
3. Run the `imu` module
    a. `python -m imu`
    b. Run `python -m imu -u` to see real-time data being collected
