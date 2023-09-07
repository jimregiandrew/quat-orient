# quat-orient

Here's the problem: You've got accelerometer data for a vehicle but you don't know this data relates to the vehicles acceleration directions (forwards/backwards and left/right cornering directions).
Here's a solution: Use GPS data and a bit of math with qaternions.

The goal of this project is to give an algorithm that solves this problem. The algorithm requires accelerometer and GPS data while the vehicle is moving - a training phase if you like. But it converges pretty quickly so that a reasonable estimate can be obtained within 10's of seconds of motion with braking and/or cornering. It's not a polished algorithm, and the python source probably isn't useable as is. But I think this is a good solution and a good base on which to make something more polished. The python code is a way of documenting the algorithm and for testing it.

If we could mount the accelerometer so that its axes matched the vehicle there would be no problem. And I suspect that this is the best solution if you are a vehicle manufacturer providing an in-build accelerometer. But if you can't control the mounting then this algorithm is one solution to the problem.

The test data was generated with an Android mobile phone mounted with Blu Tak :D to the dash in a car. The test data was generated using known orientations so that the algorithm can be verified. But it will work with an arbitrary fixed mounting orientation.

This repository contains python code and test data to determine the "best" quaternion that rotates the accelerometer vector, output by the accelerometer, to the acceleration vector of the vehicle (with axes as defined above). More generally it describes a method to find the quaternion that gives the "best" rotation to match a set of input and output (3-dimensional) vectors.

# Vehicle axes

I use the following definition of the vehicle axes: x points forwards (the direction the driver is facing), y points to the left, and z points up vertically. (It is a right hand system).

# How does it work

The math for solving the least squares registration problem, given by Yan-Bin Jia (see References) is the same for finding the quaternion rotation that best rotates a set of input vectors (accelermeter output vectors) to match a set of output vectors (the vehicles accelerometer vectors). That is the optimum quaternion is the eigenvector, corresponding to the largest eigenvalue, of a matrix formed from suitably combined input/output data. See the get_opt_q function in src/quaternions.py. 

# How to use it.
There are two trips of test data: one with date/time 2020-10-15-21 and one with 2020-10-15-22. The data/README.md file gives more information but you don't have to read it yet.

There are a few python packages to install - and I've used python3. I used a virtual environment and the following requirements file e.g. From the src directory:
```
pip3 install -r requirements.txt
```

Once these are installed run python from the command line in the src directory. Then execute the following for the first trip:

```
import quaternions as qu
q1=qu.get_opt_q_file('../data','2020-10-15-21');
```

Then you should see something like:

```
q1
[ 0.99960554 -0.01820031  0.0169176  -0.01308816]
qu.dist_degrees(q1,[1,0,0,0])
1.618
```
This quaternion is close to the identity quaternion [1,0,0,0], which effects no change (no rotation). As per data/README.md the phone was mounted on this first trip with this identity orientation (according to my eyechrometer) - that is so the phone accelerometer axes are close to the vehicle axes. And the estimated quaternion q1, rotates the data only by 2*1.618... ~= 3.2 degrees - which is indeed close to the identity.

Running the same function for the second trip (2020-10-15-22) data will result in the qaternion

```
qu.set_fixed_prec_format(4)
q2
array([-0.0039, 0.0054, 0.0043, 1.0000])
2*qu.dist_degrees(q2,[1,0,0,0])
179.5519155557356
```

This qaternion effects an approx 180 degree rotation about the z-axis (note that quaternion rotation effects a rotation of double the angle defined by it's real term). And on this return trip this was how I (re) mounted the phone, again according to my eyecrometer.

The algorithm converges pretty quickly. After 10 seconds of data (of speed > 7 kmph) it's quite a reasonable estimate as shown by:
```
import numpy as np
import quaternions as qu
faccel1,gps1 = qu.get_filtered_accel_gps_file('../data','2020-10-15-21')
q1=qu.get_opt_q_file('../data','2020-10-15-21');
for n in np.arange(50,341,10):
    q=qu.get_opt_q(faccel1,gps1[qu.time_slice(gps1,0,n),:],spd_thresh=7)
    d=2*qu.dist_degrees(q,q1)
    print(f"{n} {d:.1f}")

```

We can also calculate the optimum quaternion for data localized in time, and see how it varies over time. - e.g. a running average of the data (of the matrices, but not the accel data). This can be used to e.g. detect if the device is fixed to the vehicle or not (e.g. "rolling around on the floor"). If the device is not fixed, the orientation / optimum quaternion will likely change significantly over time.

# What are quaternions ?

Quaternions are hard to understand and I don't know them well enough to give a (good) tutorial. So these notes are for mainly for me. I learned about quaternions from the references in the References section.

I like Ken Shoemakes (see References) description where he says there are basically several different (equivalent) ways to define Quaternions. The main ways are: 

1. Hamilton's way as extended complex numbers w +ix, jy + kz (with multiplication distributive over addition, and i^2 = j^2 = k^2 = ijk = -1)
2. The more abstract way as quadruples of real numbers (w, x, y, z) - a 4D vector - with addition and multiplication suitably defined
3. Like 2. but a more compact 2-tuple (w, v) with w a scalar (real number) and v a 3 component vector (part).

Shoemake lists definitions and facts. The only thing I don't like is that he puts the vector part first in the 2-tuple, but Wikipedia and other references I found put the vector part second. I stick with the Wikipedia convention. He also gives the "rotation theorem": Given a unit quaternion q (and its conjugate q*), the multiplication qvq* rotates vector v in 3D by angle = 2*arccos(w), around the axis given by the vector part of q (Note v in this equation is a quaternion, with 0 real part).

# FAQ

Q. Why not just use GPS data, since you can (and do here) calculate forwards/backwards and cornering acceleration from it ?
A. Because gravity "leakage" into this acceleration is signifiant. Gravity ~= 9.81 m/s^2 is a massive accereration relative to usual vehiclular accelerations. And sine(theta) has maximum slope around 0 angle. So therefore gravity * sin(road slope) - the "leakage" is relatively large. For example, in the test data, the slope on Ayr street adds nearly 2 m/s^2 braking acceleration. E.g. at constant speed driving down Ayr St, the vehicle experiences a constant near 2 m/s^2 braking accceleration (force). I've braked and briefly slid at the bottom of Ayr Street because of this slope/braking acceleration (exacerbated because it was wet) without hitting the brakes hard. This gravity leakage is also why camber on corners is so important - or so bad for an off camber corner.

Q. How to contribute?
A. Please review and provide feedback. You could also collect more test data - e.g. accerlerometer and GPS data (with e.g. AndroSensor app). You do need to note the orientation of the device so we can check the results. If you write code the algorithm would be more useful in C++, Kotlin etc, for a real-time variant (that is calculate orientation on the fly as data comes in). That's not a trivial task BTW so you might want to do this under your own project.

# References

Quaternions are are hard to understand (unless you are a mathematician) - they take time and effort to learn. There are many references on the Internet on Quaternions. I collect here the ones that I used.

I started with some intuitive explanations / visualizations at:

1. https://eater.net/quaternions
2. https://www.youtube.com/watch?v=d4EgbgTm0Bg&t=1s

But I never really groked it. I found I made more progress when I looked at papers that focused on quaternion algebra - basically the algebra is the same as for real (or complex) numbers *except* quaternion multiplication is not commutative: that is for quaternions p and q, pq != qp (in general).

1. http://www.faqs.org/faqs/graphics/algorithms-faq/ # comp.grahpics.algorithms FAQ. I got the Shoemake reference from here.
2. ftp://ftp.cis.upenn.edu/pub/graphics/shoemake/ # Ken Shoemake. I really like the list of facts. There are no derivations for the facts, but most aren't too hard to show, using the definitions and quaternion algebra. Theorem 1 is good, but it took me a while to get/fill in the gaps in the proof.
3. "Quaternions and Rotations", Yan-Bin Jia # There are a few versions on the Internet, presumably a base version that grew over time
4. https://math.stackexchange.com/questions/328117/how-does-one-derive-this-rotation-quaternion-formula # Helped me follow rotation theorem proofs.
5. https://en.wikipedia.org/wiki/Triple_product # Some dot and triple product formulae are needed for the proofs (usually a given in the proofs in the references).
5. https://en.wikipedia.org/wiki/Quaternion # Wikipedia - usually worth a read
6. "Some Notes on Unit Quaternions and Rotation", Berthold K.P. Horn. https://ocw.mit.edu/courses/6-801-machine-vision-fall-2004/0a576904c8aa2add9d02df14ca85c019_quaternions.pdf # Good short summary paper. I liked the left and right product matrix description.
7. https://qr.ae/pyBRuT # Quora answer to the question "Why is the quaternion so hard to understand?" (I like this answer, if perhaps after the fact of a reasonable understanding).

