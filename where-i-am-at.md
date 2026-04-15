Where I am at. I would like to make this code more of a library one day that is used by others, or myself should I return to telematics work. For now I think that:
1. Writing the code in C, C++ or possibly rust would make it more usable in telematics?
2. I would like to explore the Kalman filtering option more (using the quaternion description). It seems to have great flexability in adapting the prediction and measurement noise. And could incorporate gyro data.
3. Doing 1 and 2 is a lot of work and I think perhaps is better done if I return to this problem later when there is a more pressing need for it (e.g. I am working in telematics)

What do you think?

Your assessment seems sound. A few thoughts:

On language choice (#1): C or Rust would make sense for embedded telematics devices. Rust has better ergonomics for the math involved and memory safety without a GC. C is more universal in embedded ecosystems. Either way, the Python version serves well as a reference/prototype — porting a working algorithm is much easier than developing one from scratch in a systems language.

On Kalman filtering (#2): Agreed this is the natural next step. A quaternion-based EKF would let you fuse accelerometer, GPS, and gyro data with proper uncertainty handling, and adapt online rather than needing batch optimization. It's also the standard approach in production IMU/AHRS systems, so there's good literature to draw from.

On timing (#3): This is the right call. The Python reference implementation captures the core algorithm and validates it against known data. That's the hard part. Porting to C/Rust and adding Kalman filtering is engineering work that's best motivated by a concrete deployment target — you'll make better design decisions when you know the actual constraints (which MCU, what sensor suite, real-time requirements, etc.).

The current codebase is in good shape as a reference. If you do return to it, you'll have working test cases and validated math to build from.