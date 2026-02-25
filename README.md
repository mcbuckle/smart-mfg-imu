# Running
In the future, there will be a dockerfile to make setup easier.
For now, you must do the following:

1. Create a python virtual environment (optional but recommended)
    a. `python -m venv .venv`
    b. Activate it:
       - Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
       - Windows CMD: `.venv\\Scripts\\activate.bat`
       - macOS/Linux: `source .venv/bin/activate`
2. Install dependencies
    a. `pip install -r requirements.txt`
3. Run the `imu` module
    a. `python -m imu`
    b. Run `python -m imu -u` to see real-time data being collected
    c. Run `python -m imu -t` to use fake/sample IMU data
    d. Run `python -m imu -t -u` to use fake/sample IMU data with UI
    e. Run `python -m imu -u --tare` to zero yaw/pitch/roll at startup

# Testing
Run unit tests with:

`python -m pytest -q`

# Output format
Each IMU sample now includes a per-session monotonically increasing `counter` that starts at `0` when the IMU process starts and increments by `1` for each generated sample.

CSV header:

`counter,capture_time_ms,recorded_at_time_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,yaw,pitch,roll`

MQTT payload order:

`counter,capture_time_ms,recorded_at_time_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,yaw,pitch,roll`

Units: `accel_*` in m/s², `gyro_*` in rad/s, and `yaw/pitch/roll` in degrees.
