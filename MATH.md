# Mathematical Background
By: Jim Andrew and assisted by Claude Code (Opus 4.6)

This document describes the mathematics behind the quaternion-based orientation estimation algorithm.

## Problem statement

An accelerometer is rigidly mounted to a vehicle in an unknown orientation. The accelerometer measures a 3D acceleration vector **a** in its own coordinate frame. We want to find the rotation that maps from the accelerometer frame to the vehicle frame, where:

- **x** = forwards (direction the driver faces)
- **y** = left
- **z** = up

If we can determine this rotation, we can transform raw accelerometer readings into meaningful vehicle accelerations (braking, cornering, etc.).

## Quaternion preliminaries

A quaternion is a 4-tuple $q = (w, x, y, z)$ where $w$ is the scalar part and $(x, y, z)$ is the vector part. Quaternion multiplication is associative and distributive but **not commutative**.

A **unit quaternion** ($\|q\| = 1$) represents a 3D rotation. Given unit quaternion $q = (\cos\frac{\theta}{2},\; \hat{n}\sin\frac{\theta}{2})$, the rotation is by angle $\theta$ about axis $\hat{n}$.

To rotate a 3D vector **v**, embed it as a pure quaternion $p = (0, \mathbf{v})$ and compute:

$$\mathbf{v}' = q\, p\, q^*$$

where $q^* = (w, -x, -y, -z)$ is the conjugate. Note that $q$ and $-q$ represent the same rotation, since $(-q)\,p\,(-q)^* = q\,p\,q^*$.

## Product matrices

Quaternion multiplication can be expressed as matrix-vector products. In the equations below, we identify a quaternion $(w, x, y, z)$ with the 4-vector $\begin{pmatrix} w \\ x \\ y \\ z \end{pmatrix}$ — these are different mathematical objects (a quaternion vs. a vector in $\mathbb{R}^4$), but they share the same four components, and quaternion multiplication is linear in each argument, so the identification works. With this convention, for quaternions $p$ and $r$:

The **left product matrix** $L(p)$ satisfies $p \cdot r = L(p)\, r$:

$$L(p) = \begin{pmatrix} p_0 & -p_1 & -p_2 & -p_3 \\ p_1 & p_0 & -p_3 & p_2 \\ p_2 & p_3 & p_0 & -p_1 \\ p_3 & -p_2 & p_1 & p_0 \end{pmatrix}$$

The **right product matrix** $R(r)$ satisfies $p \cdot r = R(r)\, p$:

$$R(r) = \begin{pmatrix} r_0 & -r_1 & -r_2 & -r_3 \\ r_1 & r_0 & r_3 & -r_2 \\ r_2 & -r_3 & r_0 & r_1 \\ r_3 & r_2 & -r_1 & r_0 \end{pmatrix}$$

Both matrices are orthogonal (up to a scale factor equal to the squared norm of the quaternion). Using these, the rotation $q\,p\,q^*$ can be written as $R(q^*)\, L(q)\, p$.

## Deriving the vehicle acceleration vector from GPS

GPS provides speed $s$ and track angle (heading) $\psi$ at each time step. From consecutive GPS readings we derive the vehicle-frame acceleration:

**Longitudinal (forward) acceleration** from the rate of change of speed:

$$a_x = \frac{s_{n+1} - s_n}{\Delta t}$$

**Lateral (centripetal) acceleration** from the rate of change of heading:

$$a_y = s \cdot \frac{\Delta\theta}{\Delta t}$$

where $\Delta\theta = -\Delta\psi$ (the sign flip accounts for the opposite rotation sense between track angle and the vehicle coordinate convention).

**Vertical acceleration** is approximately gravity when the road is level:

$$a_z \approx g = 9.81 \;\text{m/s}^2$$

This gives a GPS-derived vehicle acceleration vector $\mathbf{g_a} = (a_x, a_y, g)$ at each time step.

## The optimal rotation as an eigenvector problem

We seek the unit quaternion $q$ that best rotates the accelerometer vectors $\mathbf{a}_n$ to match the GPS-derived vehicle vectors $\mathbf{g_a}_n$. "Best" means minimizing the sum of squared residuals:

$$E(q) = \sum_n \| q\, \bar{a}_n\, q^* - \bar{g}_n \|^2$$

where $\bar{a}_n = (0, \mathbf{a}_n)$ and $\bar{g}_n = (0, \mathbf{g_a}_n)$ are pure quaternions.

We now show that minimizing $E(q)$ reduces to maximizing a quadratic form.

**Right-multiply by $q$ to linearize.** The rotation $q\bar{a}q^*$ has $q$ on both sides of $\bar{a}$, making $E$ quartic in $q$. The key trick is to right-multiply the expression inside the norm by the unit quaternion $q$, which preserves norms:

$$\|q\bar{a}q^* - \bar{g}\|^2 = \|(q\bar{a}q^* - \bar{g})\,q\|^2 = \|q\bar{a}(q^*q) - \bar{g}q\|^2 = \|q\bar{a} - \bar{g}q\|^2$$

**Rewrite using product matrices.** Since $q\bar{a} = R(\bar{a})\,q$ and $\bar{g}q = L(\bar{g})\,q$:

$$= \|\bigl(R(\bar{a}) - L(\bar{g})\bigr)\,q\|^2 = q^T\bigl(R(\bar{a}) - L(\bar{g})\bigr)^T\bigl(R(\bar{a}) - L(\bar{g})\bigr)\,q$$

**Expand.** Using orthogonality of the product matrices ($R^T R = \|\bar{a}\|^2 I$ and $L^T L = \|\bar{g}\|^2 I$), and the fact that $R(\bar{a})^T L(\bar{g})$ is symmetric when both quaternions are pure (zero scalar part, verified symbolically in [symquats.py](src/symquats.py)), so that $L(\bar{g})^T R(\bar{a}) = R(\bar{a})^T L(\bar{g})$:

$$= q^T\Bigl[(\|\bar{a}\|^2 + \|\bar{g}\|^2)\,I \;-\; 2\,R(\bar{a})^T L(\bar{g})\Bigr]\,q$$

**Drop the constant.** The term $(\|\bar{a}\|^2 + \|\bar{g}\|^2)$ does not depend on $q$, and for unit $q$ we have $q^T I\, q = 1$. So summing over all samples, minimizing $E(q)$ is equivalent to **maximizing**:

$$q^T M\, q \quad\text{subject to}\quad \|q\| = 1$$

where:

$$M = \sum_n R(\bar{a}_n)^T \, L(\bar{g}_n)$$

Here $R(\bar{a}_n)$ is the right product matrix for the pure quaternion $(0, \mathbf{a}_n)$ and $L(\bar{g}_n)$ is the left product matrix for $(0, \mathbf{g_a}_n)$.

Since $M$ is a sum of symmetric matrices, $M$ itself is real symmetric. By the Rayleigh quotient, the maximum of $q^T M q$ subject to $\|q\| = 1$ is achieved when $q$ is the **eigenvector corresponding to the largest eigenvalue** of $M$.

This is the same mathematical structure as the least-squares point registration problem described by Yan-Bin Jia and by Horn.

## Signal conditioning

The raw accelerometer data is noisy at GPS time scales. Before pairing with GPS-derived accelerations, the accelerometer signal is low-pass filtered with a 4th-order Butterworth filter (cutoff period of 17 samples). This removes high-frequency vibration while preserving the vehicle dynamics that GPS can also observe.

GPS samples where speed is below a threshold (default 7 km/h) are excluded, since at low speeds the heading is unreliable and the acceleration signals are dominated by noise.

## Angular distance between quaternions

The angular distance between two unit quaternions $q_1$ and $q_2$ is:

$$d = \arccos(|q_1 \cdot q_2|)$$

This gives **half** the rotation angle between the two orientations (because a quaternion encodes half the rotation angle in its scalar part). The full rotation angle is $2d$.

The absolute value handles the $q \equiv -q$ equivalence.

## Summary

1. Low-pass filter the accelerometer data
2. Derive vehicle-frame acceleration vectors from GPS (speed, heading, gravity)
3. At each GPS time step, form the $4\times4$ matrix $R(\bar{a})^T L(\bar{g})$ and accumulate into $M$
4. Find the eigenvector of $M$ with the largest eigenvalue
5. This eigenvector is the optimal unit quaternion mapping accelerometer frame to vehicle frame
