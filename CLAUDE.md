# CLAUDE.md

## Project overview

Determines the orientation of an accelerometer relative to a vehicle's axes using quaternions and GPS data. The algorithm finds the optimal quaternion rotation that maps accelerometer readings to vehicle acceleration vectors (derived from GPS). Written in Python as a reference implementation and test harness.

## Project structure

- `src/quaternions.py` - Core algorithm: quaternion math, data loading, optimal quaternion estimation
- `src/symquats.py` - Symbolic quaternion utilities
- `data/` - Test trip CSV files (accelerometer and GPS data from two known-orientation trips)
- `tests/` - Smoke tests verifying algorithm correctness against known orientations

## Setup

This project uses `uv` for dependency management. Python 3.13+.

```
uv sync
```

## Running tests

```
uv run python tests/test_orientation.py
```

## Key functions in src/quaternions.py

- `get_opt_q(faccel, gps, spd_thresh)` - Computes optimal rotation quaternion from filtered accelerometer and GPS data
- `get_opt_q_file(dir_in, date, spd_thresh)` - Loads data from CSV files and calls `get_opt_q`
- `dist_degrees(q1, q2)` - Angular distance between two quaternions in degrees (half-angle; multiply by 2 for full rotation)

## Conventions

- Vehicle axes: x = forwards, y = left, z = up (right-hand system)
- Quaternions use [w, x, y, z] ordering (scalar first)
- `dist_degrees` returns half the rotation angle; the full rotation is `2 * dist_degrees(q, [1,0,0,0])`
