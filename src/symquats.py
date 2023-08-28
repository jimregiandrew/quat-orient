import sympy
from sympy import symbols
from sympy import Quaternion
from sympy import Matrix
p0=symbols('p0'); p1=symbols('p1'); p2=symbols('p2'); p3=symbols('p3'); 
p = Quaternion(p0, p1, p2, p3)
q0=symbols('q0'); q1=symbols('q1'); q2=symbols('q2'); q3=symbols('q3'); 
q = Quaternion(q0, q1, q2, q3)
p*q

#>>> r.a
#p0*q0 - p1*q1 - p2*q2 - p3*q3
#>>> r.b
#p0*q1 + p1*q0 + p2*q3 - p3*q2
#>>> r.c
#p0*q2 - p1*q3 + p2*q0 + p3*q1
#>>> r.d
#p0*q3 + p1*q2 - p2*q1 + p3*q0

P = Matrix([[p0,-p1,-p2,-p3], [p1,p0,-p3,p2], [p2,p3,p0,-p1], [p3,-p2,p1,p0]])
Q = Matrix([[q0,-q1,-q2,-q3], [q1,q0,q3,-q2], [q2,-q3,q0,q1], [q3,q2,-q1,q0]])

# Results verified against https://people.csail.mit.edu/bkph/articles/Quaternions.pdf
# (https://ocw.mit.edu/courses/6-801-machine-vision-fall-2004/0a576904c8aa2add9d02df14ca85c019_quaternions.pdf)

# Note P and Q are orthogonal. That is P*P.transpose() = P.transpose()*P = eye(4) * C, where C = p0**2 + p1**2 + p2**2 + p3**2
#(In the python command line set: p0=quaternions.p0;p1=quaternions.p1;p2=quaternions.p2;p3=quaternions.p3;P=quaternions.P;Q=quaternions.Q)
# Can verify with: (p0**2 + p1**2 + p2**2 + p3**2) * np.eye(4) - P.transpose()*P
# Also Q.transpose()*P and P.transpose()*Q are symmetric **when** p0=q0=0. Verified with:
# S=P.transpose()*Q; D=S - S.transpose(); D.subs(q0,0).subs(p0,0)

