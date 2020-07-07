"""This class is a handler and interfaces between the GUI and the motor clasess.
It translates all the basic commands into motor-class based code.
Commands are:
move - forward backward
rvel - revolve
head - goto compass bearing
stop - stop
left - move left wheel only
right - move right wheel only"""

from rerobot.motor import Motor

class Robot():

    def __init__(self):
        self.motor = Motor()

    def move(self, dist=10):
        """Translate (+) forward or (-) back mm distance at SETV speed"""
        self.motor.cmd(cmd=8, value=dist)

    def rvel(self, speed=10):
        """Rotate robot at (+) counter- or (–) clockwise; degrees/sec (SETRV limit)."""
        self.motor.cmd(cmd=21, value=speed)

    def head(self, degree=0):
        """Turn at SETRV speed to absolute heading; ±degrees (+ = ccw )"""
        self.motor.cmd(cmd=12, value=degree)

    def rotate(self, degrees=10):
        """Rotate (+) counter- or (-) clockwise degrees/sec."""
        self.motor.cmd(cmd=9, value=degrees)

    def stop(self):
        self.motor.stop()

    def left(self, speed=1.0):
        self.motor.left(speed)

    def right(self, speed=1.0):
        self.motor.right(speed)

    def terminate(self):
        self.motor.terminate()

# todo set motor and translations speeds via GUI

    # def set_motors(self, left_speed, right_speed):
    #     self.left_motor.value = left_speed
    #     self.right_motor.value = right_speed

