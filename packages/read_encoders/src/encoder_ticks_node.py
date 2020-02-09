#!/usr/bin/env python

import os
import rospy
from duckietown import DTROS
from read_encoders.msg import encoderTicksStamped
from std_msgs.msg import Header
import pigpio
#from std_msgs.msg import String

# Global
#pi = 3.14
pi = pigpio.pi()
cb1 = pi.callback(18, pigpio.RISING_EDGE)
cb2 = pi.callback(19, pigpio.RISING_EDGE)


class MyNode(DTROS):

    def __init__(self, node_name):
        # initialize the DTROS parent class
        super(MyNode, self).__init__(node_name=node_name)
        # construct publisher
        self.pub = rospy.Publisher('encoder_ticks', encoderTicksStamped, queue_size=1)
	# Note: Update to include to islduckie44/wheels_driver_node/wheels_cmd_executed to check the direction of the wheels 
	# ... so the encoder ticks can be incremented or decremented
	self.msg = encoderTicksStamped() # Following the Duckietown convention


	# Relate pi to the pigpio interface
	self.pi = pigpio.pi()

	self.left_motor_pin = 18
	self.right_motor_pin = 19

	# Setup the callbacks for each io pin
	global cb1
	global cb2
	cb1 = self.pi.callback(self.left_motor_pin, pigpio.RISING_EDGE, self.cbPublish())
	cb2 = self.pi.callback(self.right_motor_pin, pigpio.RISING_EDGE, self.cbPublish())


    def cbPublish(self):
	# Publishes both sets of encoder ticks whenver a tick is registered
	global cb1
	global cb2

	self.msg.header.stamp = rospy.get_rostime()
	self.msg.left_ticks = cb1.tally()
	self.msg.right_ticks = cb2.tally()
	self.pub.publish(self.msg)
	rospy.loginfo("Published %d %d" % (self.msg.left_ticks, self.msg.right_ticks))


    def run(self):
        # publish message every 1 second
        rate = rospy.Rate(1000) # Hz
	# self.msg = encoderTicksStamped() # Defined in __init__

	# Establish timing for reporting rospy.loginfo updates
        now = rospy.get_rostime()
        secs = now.secs
        wait_time = 1

        global cb1
        global cb2
	self.lastcb1 = cb1.tally()
	self.lastcb2 = cb2.tally()


        while not rospy.is_shutdown():
            if ((cb1.tally() != self.lastcb1) or (cb2.tally() != self.lastcb2)):
                self.lastcb1 = cb1.tally(); self.lastcb2 = cb2.tally()
                self.pi.callback(self.left_motor_pin,  pigpio.RISING_EDGE, self.cbPublish())


            rate.sleep()




if __name__ == '__main__':
    # create the node
    node = MyNode(node_name='my_node')
    # run node
    node.run()
    # keep spinning
    rospy.spin()