# quat-orient

This repository contains python code, test data and a description of how to determine the orientation of an accelerometer, relative the the vehicle in which it is mounted. The python code finds the "best" quaternion to rotate the 3-axis accelerometer data to match the GPS derived acceleration data. This is an estimate of the accelerometers orientation.

# How does it work

See the get_opt_q function in src/quaternions.py.

# How to use it.
Run python from the command line in the src directory. Then execute:

import quaternions as qu
q1=qu.get_opt_q('/home/jim/src/quat-orient/data','2020-10-15-21');

Then you should see something like:

q= [ 0.99960554 -0.01820031  0.0169176  -0.01308816] angle= 1.6093524883213315 degrees

This quaternion is close to a null rotation (i.e. rotated data = input data). It rotates the data only by 2*1.609... ~= 3.2 degrees.

Running the same function for the 2020-10-15-22 data will result in a qaternion that is (in effect) close to a 180 degree rotation.
