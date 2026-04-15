# Kalman Filter Approach to Orientation Estimation

## What is a Kalman filter?

A Kalman filter is a general estimation framework for combining uncertain information over time. The core idea:

> You have a **belief** about some state (with uncertainty). A new **measurement** arrives (also uncertain). You blend them, weighting each by how confident you are in it. Repeat.

The filter is independent of any particular problem formulation — it doesn't care whether your state is a quaternion, Euler angles, a rotation matrix, or something entirely unrelated to rotations. You supply the contents; the filter provides the machinery.

## Your problem as context

Your current approach in get_opt_q is a batch method: you accumulate the matrix M over all GPS/accel pairs, then find the best quaternion at the end via eigendecomposition. Every data point gets equal weight. You process the whole trip, then get one answer.

A Kalman filter would instead give you a running estimate of the orientation quaternion that updates with each new GPS/accel pair, getting more confident over time.

## The three components you supply

1. **State** — what you're estimating, plus how uncertain you are (a covariance matrix P). For you: the quaternion q = [w, x, y, z] mapping accelerometer frame to vehicle frame. Your uncertainty is a covariance matrix P (a 4x4 or 3x3 matrix if you parameterize rotations with e.g. Rodrigues vectors to avoid quaternion constraints).
2. **Prediction model** — how the state evolves over time (for a fixed mount: it doesn't)
3. **Measurement model** — how observations relate to the state (here: `rotate(q, accel) ≈ gps_accel`)

Plus two noise parameters:
- **Q** (process noise) — how much the state might drift per step
- **R** (measurement noise) — how noisy the measurements are

## The three steps (repeating each timestep)

### 1. Predict

Apply the dynamics model. For a fixed sensor mount, the quaternion doesn't change, so prediction is trivial:

```
q_predicted = q_previous
P_predicted = P_previous + Q
```

Q is small — it just says "I'm slightly less sure than I was."

### 2. Compute innovation (residual)

Compare what we'd expect to measure (given our current estimate) to what we actually measured:

```
y = gps_accel - rotate(q_predicted, accel)
```

### 3. Update

Blend the prediction with the measurement using the Kalman gain K:

```
K = P * H' * (H * P * H' + R)^{-1}
q_new = q_predicted + K * y
P_new = (I - K * H) * P_predicted
```

Where H is the Jacobian of the measurement function w.r.t. the state.

### Why K is the key insight

- **R large** (noisy GPS) → K small → trust existing estimate, mostly ignore measurement
- **P large** (uncertain state) → K large → weight measurement heavily
- Early on, P is large so measurements pull the estimate around. Over time, P shrinks and the estimate stabilises. This is just Bayesian updating.

## "Extended" Kalman Filter (EKF)

Because `rotate(q, accel)` is nonlinear in q, we use an Extended Kalman Filter, which linearises the measurement function by computing its Jacobian H at each step. The standard Kalman filter assumes linear models; the EKF relaxes this at the cost of approximate (rather than optimal) updates.

## Batch method vs Kalman filter

| Batch (`get_opt_q`) | Kalman filter (`kalman.py`) |
|---|---|
| One answer at end of trip | Running estimate at every timestep |
| All points weighted equally | Noisy points automatically downweighted |
| Needs full dataset in memory | Online — works sample by sample |
| Simpler to implement | More complex, but more flexible |
| Optimal (eigendecomposition) | Approximate (linearisation) |

For post-processing full trip files, the batch eigendecomposition is simpler and optimal. A Kalman filter makes more sense for:
- **Real-time** orientation estimation during a trip
- **Variable noise** (e.g., GPS accuracy changes between open sky and urban canyon)
- **Fusion** with additional sensors (gyroscope, magnetometer)

## Implementation notes (`src/kalman.py`)

### Initialisation

A single accel/GPS vector pair has rotational ambiguity (the eigenvalues of the single-pair M matrix are degenerate). Starting the EKF from identity `[1,0,0,0]` works for small rotations but fails for large ones (e.g., 180° — the linearisation can't bridge that gap). The implementation seeds from a mini-batch of the first 10 valid data points to break this ambiguity.

### Tuning

- `process_noise` (default `1e-6`): for a rigid mount, keep very small. Increase if the sensor can shift.
- `measurement_noise` (default `1.0`): reflects GPS-derived acceleration noise in (m/s²)². Decrease to trust GPS more; increase in noisy conditions.

### Results

On the two test trips, the EKF agrees with the batch method to within ~2–4°.
