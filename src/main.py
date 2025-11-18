# This file kept solely for backwards compatibility
import sys

print("It seems you have tried to run the program with the old command")
print("Please instead run:")
print("python -m imu " + " ".join(sys.argv[1:]))
