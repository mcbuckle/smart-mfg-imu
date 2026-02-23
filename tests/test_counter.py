from imu.DataWriter import DataWriter
from imu.FakeIMU import FakeIMU
from imu.IMUData import IMUData


class DummyClient:
    IMU = "IMU"

    def __init__(self, *args, **kwargs):
        self.messages = []

    def publish(self, payload: str):
        self.messages.append(payload)

    def disconnect(self):
        return None


def test_fake_imu_counter_starts_at_zero_and_increments():
    imu = FakeIMU(sample_filename="data/sample_data.csv")
    first_sample = imu.read_data()
    second_sample = imu.read_data()

    assert first_sample.counter == 0
    assert second_sample.counter == 1

    imu.file.close()


def test_data_writer_includes_counter_in_csv_and_mqtt(monkeypatch, tmp_path):
    monkeypatch.setattr("imu.DataWriter.Client", DummyClient)

    output_csv = tmp_path / "imu_output.csv"

    with DataWriter(csv_fname=str(output_csv)) as writer:
        sample = IMUData(
            1523,
            1711111111111,
            0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
            8.0,
            9.0,
            10.0,
            11.0,
            12.0,
        )

        writer.write_data(sample)

        assert writer.mqtt_client.messages[0].startswith("1523,")
        mqtt_fields = writer.mqtt_client.messages[0].split(",")
        assert mqtt_fields[0] == "1523"
        assert mqtt_fields[1] == "1711111111111"
        assert int(mqtt_fields[2]) >= 1711111111111

    lines = output_csv.read_text(encoding="utf-8").splitlines()

    assert lines[0] == "counter,capture_time_ms,recorded_at_time_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,yaw,pitch,roll"
    csv_fields = lines[1].split(",")
    assert csv_fields[0] == "1523"
    assert csv_fields[1] == "1711111111111"
    assert int(csv_fields[2]) >= 1711111111111
