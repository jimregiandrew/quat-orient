# quat-orient

The 3-axis acceleration (vector) of a vehicle is useful a variety of purposes. The one I am most familiar with is driver behavior. We can use a smart phone - or any device with an accelerometer in it - mounted in the vehicle, to measure the acceleration. The problem is that in general we don't know the orientation of the mounted device (accelerometer), and therefore don't know the direction of the (accelerometer's) acceleration vector, relative to the vehicle. This project provides an algorithm to estimate the orientation of the device relative to the vehicle, using GPS and accelerometer data.

In this project I use the following definition of the vehicle axes: x points forwards (the direction the driver is facing), y points to the left, and z points up vertically. More details can be found in the quaternions.py file.

This repository contains python code and test data to determine the "best" quaternion that represents the relative orientation of the device with respect to the vehicle.

# How does it work

See the get_opt_q function in src/quaternions.py. The math for solving the least squares registration problem, given by Yan-Bin Jia (see References) is the same for finding the quaternion rotation that best matches a set on input vectors (set of accelermeter output vectors) to output vectors (corresponding set of the vehicles accelerometer vectors). That is the optimum quaternion is the eigenvector, corresponding to the largest eigenvalue, of a matrix formed from the input/output matched data.

# How to use it.
Run python from the command line in the src directory. Then execute:

```
import quaternions as qu
q1=qu.get_opt_q('../data','2020-10-15-21');
```

Then you should see something like:

```
q= [ 0.99960554 -0.01820031  0.0169176  -0.01308816] angle= 1.6093524883213315 degrees
```
This quaternion is close to a null rotation (i.e. rotated data = input data). It rotates the data only by 2*1.609... ~= 3.2 degrees.

Running the same function for the 2020-10-15-22 data will result in the qaternion

```
q= [-0.00391026  0.00537421  0.00434894  0.99996846] angle= 90.22404222213221 degrees
```

This qaternion effects a (approx) 180 degree rotation about the z-axis (note that quaternion rotation effects a rotation of double the angle defined by it's real term).

# What are quaternions

I don't know Quaternions well enough to do a good job. So these notes are for mainly for me:

I like Shoemakes description where he says there are basically several different ways to define Quaternions. The main ways are Hamilton's way as extended complex numbers w +ix, jy + kz (with multiplication distributive over addition, and i**2 = j**2 = k**2 = ijk = -1); the more abstract way of quadruples of real numbers (w, x, y, z), with addition and multiplication suitably defined; or the more compact was as a 2-tuple (w, v) with w a scalar (real number) and v a 3 component vector (part). Shoemake lists definitions and facts. The only think I don't like is that he puts the vector part first in the 2-tuple, but Wikipedia and other references I found put the vector part second. I stick with the Wikipedia convention.

# References

Quaternions are are hard to understand (unless you are a mathematician). There are many references on the Internet on Quaternions. I collect here the ones that I used.

I started with some intuitive explanations / visualizations at:

1. https://eater.net/quaternions
2. https://www.youtube.com/watch?v=d4EgbgTm0Bg&t=1s

But I never really groked it. I found I made more progress when I looked at papers that focused on quaternion algebra - basically the algebra is the same as for real (or complex) numbers *except* quaternion multiplication is not commutative: pq != qp (in general).

1. http://www.faqs.org/faqs/graphics/algorithms-faq/ # comp.grahpics.algorithms FAQ. I got the Shoemake reference from here.
2. ftp://ftp.cis.upenn.edu/pub/graphics/shoemake/ # Ken Shoemake. I really like the list of facts but there is no derivations. Theorem 1 is good, but it took me a while to get/fill in the gaps in the proof.
3. "Quaternions and Rotations", Yan-Bin Jia # There are a few versions on the Internet, presumably a base version that grew over time
4. https://math.stackexchange.com/questions/328117/how-does-one-derive-this-rotation-quaternion-formula to derive # Helped me follow rotation theorem proofs.
5. https://en.wikipedia.org/wiki/Triple_product # Some dot and triple product formulae are very helpful for the proofs (usually a given in the proofs given).
5. https://en.wikipedia.org/wiki/Quaternion # Wikipedia - always worth a read
6. "Some Notes on Unit Quaternions and Rotation", Berthold K.P. Horn. https://ocw.mit.edu/courses/6-801-machine-vision-fall-2004/0a576904c8aa2add9d02df14ca85c019_quaternions.pdf # Good short summary paper. I liked the left and right product matrix description.
7. https://qr.ae/pyBRuT # Quora answer to the question "Why is the quaternion so hard to understand?" (I like this answer, if perhaps after the fact of a reasonable understanding).

