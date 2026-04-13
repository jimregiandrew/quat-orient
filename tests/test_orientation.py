import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
DATA = os.path.join(ROOT, 'data')

import quaternions as qu


def rotation_degrees_q(date):
    q = qu.get_opt_q_file(DATA, date)
    return 2 * qu.dist_degrees(q, [1, 0, 0, 0])


def test_q1_rotation_close_to_zero():
    deg = rotation_degrees_q('2020-10-15-21')
    assert deg < 5, f"Expected near 0 degrees, got {deg:.2f}"
    return deg


def test_q2_rotation_close_to_180():
    deg = rotation_degrees_q('2020-10-15-22')
    assert abs(deg - 180) < 5, f"Expected near 180 degrees, got {deg:.2f}"
    return deg


if __name__ == '__main__':
    deg1 = test_q1_rotation_close_to_zero()
    print(f"PASS: q1 rotation close to 0 degrees (actual: {deg1:.2f})")
    deg2 = test_q2_rotation_close_to_180()
    print(f"PASS: q2 rotation close to 180 degrees (actual: {deg2:.2f})")
    print("All tests passed.")
