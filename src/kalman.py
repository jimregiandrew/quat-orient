"""
Extended Kalman Filter for estimating accelerometer-to-vehicle orientation quaternion.

Iteratively estimates the same rotation quaternion as quaternions.get_opt_q(),
but processes data points one at a time with tunable noise parameters.
"""

import math
import numpy as np
from scipy import signal
import quaternions as qu


def rotation_jacobian(q, a):
    """
    Jacobian of rotate(q, a) with respect to q.
    rotate(q, a) = q * [0,a] * q*  — derivative is a 3x4 matrix (3 output components, 4 quaternion components).
    """
    w, x, y, z = q
    ax, ay, az = a

    # d(rotate)/dq — derived from expanding q * [0,a] * q*
    H = 2 * np.array([
        [ w*ax - z*ay + y*az,  x*ax + y*ay + z*az,  -y*ax + x*ay + w*az, -z*ax - w*ay + x*az],
        [ z*ax + w*ay - x*az,  y*ax - x*ay - w*az,   x*ax + y*ay + z*az,  w*ax - z*ay + y*az],
        [-y*ax + x*ay + w*az,  z*ax + w*ay - x*az,  -w*ax + z*ay - y*az,  x*ax + y*ay + z*az],
    ])
    return H


class QuaternionEKF:
    def __init__(self, process_noise=1e-6, measurement_noise=1.0, q_init=None):
        """
        process_noise: scalar for Q diagonal — how much the orientation might drift per step.
                       For a fixed mount, keep this very small.
        measurement_noise: scalar for R diagonal — how noisy the GPS-derived accelerations are (m/s²)².
        q_init: initial quaternion estimate [w,x,y,z]. If None, uses identity.
        """
        if q_init is not None:
            self.q = np.array(q_init, dtype=float)
            self.q /= np.linalg.norm(self.q)
        else:
            self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.P = np.eye(4) * 10.0                  # large initial uncertainty
        self.Q_noise = np.eye(4) * process_noise
        self.R_noise = np.eye(3) * measurement_noise
        self.num_updates = 0

    def predict(self):
        """Predict step — orientation is static, so q unchanged, P grows slightly."""
        # q_predicted = q (no dynamics)
        self.P = self.P + self.Q_noise

    def update(self, accel, gps_accel):
        """
        Update step with one accelerometer/GPS-acceleration pair.
        accel: 3-element array [ax, ay, az] in sensor frame
        gps_accel: 3-element array [ax, ay, g] in vehicle frame (forward, left, up)
        """
        self.predict()

        # Expected measurement: rotate(q, accel) should equal gps_accel
        expected = qu.rotate(self.q, accel)
        y = gps_accel - expected  # innovation

        H = rotation_jacobian(self.q, accel)

        S = H @ self.P @ H.T + self.R_noise  # innovation covariance
        K = self.P @ H.T @ np.linalg.inv(S)  # Kalman gain

        self.q = self.q + K @ y
        self.q = self.q / np.linalg.norm(self.q)  # re-normalize

        I4 = np.eye(4)
        self.P = (I4 - K @ H) @ self.P

        self.num_updates += 1

    def get_quaternion(self):
        return self.q.copy()

    def get_covariance(self):
        return self.P.copy()


def get_opt_q_ekf(faccel, gps, spd_thresh=7, process_noise=1e-6, measurement_noise=1.0,
                  print_diag=False):
    """
    EKF equivalent of quaternions.get_opt_q().
    Returns the final quaternion estimate after processing all data points.
    """
    t_accel = faccel[:, 0]
    gpsAccel = qu.accels_from_gpss(gps)
    g = 9.81

    # Seed the EKF with an initial estimate from first N valid points (mini-batch)
    # A single vector pair has rotational ambiguity; a few points break it.
    seed_n = 10
    M_seed = np.zeros((4, 4))
    seed_count = 0
    for n in range(gpsAccel.shape[0]):
        a_idx = np.argmax(t_accel > gpsAccel[n, 0]) - 1
        a = faccel[a_idx, 1:]
        ga = np.append(gpsAccel[n, 1:], g)
        spd = (gps[n, 3] + gps[n + 1, 3]) / 2
        if spd < spd_thresh or np.isnan(a).any() or np.isnan(ga).any():
            continue
        P = qu.product_matrix_right(0, a[0], a[1], a[2])
        Q = qu.product_matrix_left(0, ga[0], ga[1], ga[2])
        M_seed += P.T @ Q
        seed_count += 1
        if seed_count >= seed_n:
            break
    vals, vecs = np.linalg.eigh(M_seed)
    q_init = vecs[:, np.argmax(vals)]

    ekf = QuaternionEKF(process_noise=process_noise, measurement_noise=measurement_noise,
                        q_init=q_init)

    for n in range(gpsAccel.shape[0]):
        a_idx = np.argmax(t_accel > gpsAccel[n, 0]) - 1
        a = faccel[a_idx, 1:]
        ga = np.append(gpsAccel[n, 1:], g)
        spd = (gps[n, 3] + gps[n + 1, 3]) / 2
        if spd < spd_thresh or np.isnan(a).any() or np.isnan(ga).any():
            continue
        ekf.update(a, ga)

    if print_diag:
        print(f"EKF: {ekf.num_updates} updates")
        print(f"q = {ekf.q}")
        print(f"angle = {np.arccos(np.clip(ekf.q[0], -1, 1)) * 180 / math.pi:.2f} degrees")
        print(f"P diag = {np.diag(ekf.P)}")

    return ekf.q


def get_opt_q_ekf_file(dir_in, date, spd_thresh=7, **kwargs):
    """File-loading wrapper, matching quaternions.get_opt_q_file() interface."""
    faccel, gps = qu.get_filtered_accel_gps_file(dir_in, date)
    return get_opt_q_ekf(faccel, gps, spd_thresh, **kwargs)


if __name__ == '__main__':
    import os
    DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

    for date in ['2020-10-15-21', '2020-10-15-22']:
        print(f"\n=== {date} ===")

        # Batch method
        q_batch = qu.get_opt_q_file(DATA, date, spd_thresh=7)
        batch_deg = 2 * qu.dist_degrees(q_batch, [1, 0, 0, 0])
        print(f"Batch:  q={q_batch}, rotation={batch_deg:.2f} deg")

        # EKF method
        q_ekf = get_opt_q_ekf_file(DATA, date, spd_thresh=7, print_diag=True)
        ekf_deg = 2 * qu.dist_degrees(q_ekf, [1, 0, 0, 0])
        print(f"EKF:    q={q_ekf}, rotation={ekf_deg:.2f} deg")

        # Compare
        diff = 2 * qu.dist_degrees(q_batch, q_ekf)
        print(f"Difference between methods: {diff:.2f} deg")
