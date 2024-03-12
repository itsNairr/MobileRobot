import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import sys
import math
import time
import numpy as np
import busio
import board
from scipy.interpolate import griddata
from adafruit_amg88xx import AMG88XX

class ThermalSensorPublisher(Node):

    def __init__(self):
        super().__init__('thermal_sensor_publisher')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'thermal_data', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.sensor = AMG88XX(self.i2c_bus)
        self.min_temp = 10.0
        self.max_temp = 70.0
        self.color_depth = 1024

    def timer_callback(self):
        pixels = []
        for row in self.sensor.pixels:
            pixels = pixels + row
        pixels = [self.map_value(p, self.min_temp, self.max_temp, 0, self.color_depth - 1) for p in pixels]

        msg = Float32MultiArray()
        msg.data = pixels
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing thermal data: "%s"' % msg.data)

    def map_value(self, x_value, in_min, in_max, out_min, out_max):
        return (x_value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def main(args=None):
    rclpy.init(args=args)
    thermal_sensor_publisher = ThermalSensorPublisher()
    rclpy.spin(thermal_sensor_publisher)
    thermal_sensor_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
