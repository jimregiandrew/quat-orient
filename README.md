# quat-orient

Measuring the acceleration (3 axis vector) of a vehicle is useful a variety of purposes. The one I am most familiar with is driver behavior. We can use a smart phone - or any device with an accelerometer in it - mounted in the vehicle, to measure the acceleration. The problem is that in general we don't know the orientation of the mounted device (accelerometer), and therefore don't know the direction of the (accelerometer's) acceleration vector, relative to the vehicle. This project provides an algorithm to estimate the orientation of the device relative to the vehicle, using GPS and accelerometer data.

In this project I use the following definition of the vehicle axes: x points forwards (the direction the driver is facing), y points to the left, and z points up vertically.

This repository contains python code and test data to determine the "best" quaternion that represents the relative orientation of the device with respect to the vehicle. Equivalently, it finds the quaternion that rotates the accelerometer vector output by the accelerometer to a vector that best matches the acceleration vector of the vehicle (with axes as defined above).

# How does it work

See the get_opt_q function in src/quaternions.py. The math for solving the least squares registration problem, given by Yan-Bin Jia (see References) is the same for finding the quaternion rotation that best rotates a set of input vectors (accelermeter output vectors) to match a set of output vectors (the vehicles accelerometer vectors). That is the optimum quaternion is the eigenvector, corresponding to the largest eigenvalue, of a matrix formed from suitably combined the input/output data.

# How to use it.
Read the data/README.md file for a description of the test data.

Run python from the command line in the src directory. Then execute:

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
This quaternion is close to the identity quaternion [1,0,0,0], which effects no change (rotation). q1 rotates the data only by 2*1.618... ~= 3.2 degrees. As per data/README.md the phone was mounted, according to my eyechrometer, with this identity orientation - that is so that the phone accelerometer axes match the vehicle axes.

Running the same function for the 2020-10-15-22 data will result in the qaternion

```
qu.set_fixed_prec_format(4)
q2
array([-0.0039, 0.0054, 0.0043, 1.0000])
2*qu.dist_degrees(q2,[1,0,0,0])
179.5519155557356
```

This qaternion effects an approx 180 degree rotation about the z-axis (note that quaternion rotation effects a rotation of double the angle defined by it's real term). And on this return trip this was how I (re) mounted the phone, using my eyecrometer.

This algorithm converges pretty quickly. After 10 seconds of data (of speed > 7 kmph) it's quite a reasonable estimate as shown by:
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

We can also calculate the optimum quaternion for data localized in time, and see how it varies over time. - e.g. a running average of the data (of the matrices, but not the accel data). This can be used to e.g. detect if the device is fixed to the vehicle or not (e.g. "rolling around"). If it's not fixed, the orientation / optimum quaternion will likely change significantly over time.

# What are quaternions

I don't know quaternions well enough to give a good tutorial. So these notes are for mainly for me. I learned about quaternions from the references in the References section.

I like Ken Shoemakes (see References) description where he says there are basically several different ways to define Quaternions. The main ways are: Hamilton's way as extended complex numbers w +ix, jy + kz (with multiplication distributive over addition, and i^2 = j^2 = k^2 = ijk = -1); the more abstract way as quadruples of real numbers (w, x, y, z), with addition and multiplication suitably defined; or the similar more compact way as a 2-tuple (w, v) with w a scalar (real number) and v a 3 component vector (part). Shoemake lists definitions and facts. The only think I don't like is that he puts the vector part first in the 2-tuple, but Wikipedia and other references I found put the vector part second. I stick with the Wikipedia convention.

# References

Quaternions are are hard to understand (unless you are a mathematician) - that is they take time and effort to learn. There are many references on the Internet on Quaternions. I collect here the ones that I used.

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

