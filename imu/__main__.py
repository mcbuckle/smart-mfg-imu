import argparse
from curses import window, wrapper

from .BaseIMU import BaseIMU
from .readings import attended_reading, unattended_reading


def ui(scr: window, imu: BaseIMU):
    scr.clear()
    scr.addstr(
        0,
        0,
        "Press any key to start capturing data",
    )
    _ = scr.getch()

    scr.erase()

    attended_reading(scr, imu)


def no_ui(imu: BaseIMU):
    unattended_reading(imu)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--ui", help="Run the program in ui mode", action="store_true"
    )
    parser.add_argument(
        "-t",
        "--test",
        help="Run the program in test mode, which does not require a physical IMU connection",
        action="store_true",
    )
    parser.add_argument(
        "--tare",
        help="Tare (zero) yaw/pitch/roll immediately after IMU connection",
        action="store_true",
    )
    args = parser.parse_args()

    if args.test:
        from .FakeIMU import IMU
    else:
        from .RealIMU import IMU

    imu = IMU.get_conn()

    if args.tare and hasattr(imu, "tare"):
        imu.tare()

    if args.ui:
        wrapper(ui, imu)
    else:
        no_ui(imu)
