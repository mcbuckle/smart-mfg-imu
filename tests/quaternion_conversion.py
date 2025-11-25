from imu.FakeIMU import IMU


def test_quat():
    imu = IMU.get_conn()

    convert = imu._quat_to_ypr

    preset_quats = [
        (1, 0, 1, 0),
        (1, 0, 0, 1),
        (1, 1, 1, 1),
        (-1, -1, -1, -1),
        (-1, 0, -1, 0),
        (-1, 0, 0, -1),
    ]

    preset_ypr = [
        (0, 90, 0),
        (0,0,90),
        (90,0,90),
        (90,0,90),
        (0,90,0),
        (0,0,90)
    ]

    for q, res in zip(preset_quats, preset_ypr):
        x = convert(q)
        print(x)
        assert x == res
