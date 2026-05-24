import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import serial
import time

class MotorNode(Node):
    def __init__(self):
        super().__init__('motor_node')
        
        # Setup Serial Connection
        self.arduino_port = '/dev/ttyUSB0'
        self.baud_rate = 57600
        
        try:
            self.ser = serial.Serial(self.arduino_port, self.baud_rate, timeout=1)
            time.sleep(3) # 2-3 seconds for arduino to boot
            self.ser.write(b'r\r') # Reset encoders on startup
            self.get_logger().info("Successfully connected to Arduino!")
        except serial.SerialException as e:
            self.get_logger().error(f"Serial Error: {e}")
            return

        # 3. Create a Publisher: Shouts encoder data at 10Hz
        self.encoder_pub = self.create_publisher(String, 'encoder_ticks', 10)
        self.timer = self.create_timer(0.1, self.read_encoders) # 0.1 seconds = 10Hz

        # 4. Create a Subscriber: Listens for ROS 2 driving commands
        self.cmd_sub = self.create_subscription(Twist, 'cmd_vel', self.drive_robot, 10)
        
        self.get_logger().info("Motor Node is running and listening for commands...")

    def read_encoders(self):
        """ This runs 10 times a second to ask the Arduino for ticks """
        if self.ser.is_open:
            self.ser.write(b'e\r')
            response = self.ser.readline().decode('utf-8').strip()
            
            if response:
                # Create a ROS String message and publish it
                msg = String()
                msg.data = response
                self.encoder_pub.publish(msg)
                # Check if it's working
                self.get_logger().info(f"Published Ticks: {response}")

    def drive_robot(self, msg):
        forward_speed = msg.linear.x
        turn_speed = msg.angular.z

        linear_scale = 50.0
        angular_scale = 15.0

        left_target = (forward_speed * linear_scale) - (turn_speed * angular_scale)
        right_target = (forward_speed * linear_scale) + (turn_speed * angular_scale)

        command = f"m {int(left_target)} {int(right_target)}\r"
        if self.ser.is_open:
            self.ser.write(command.encode('utf-8'))
            self.get_logger().info(f"Sent to Arduino: {command.strip()}")

def main(args=None):
    rclpy.init(args=args)
    
    # Fire up the node
    node = MotorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        if hasattr(node, 'ser') and node.ser.is_open:
            node.ser.write(b'm 0 0\r') # Emergency stop
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
