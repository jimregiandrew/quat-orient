import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from scipy import signal; 

def product_matrix_left(*args):
    p = args[0] if hasattr(args[0], "__len__")  else args
    p0 = p[0]
    p1 = p[1]
    p2 = p[2]
    p3 = p[3]
    return np.array([[p0,-p1,-p2,-p3], [p1,p0,-p3,p2], [p2,p3,p0,-p1], [p3,-p2,p1,p0]])

def product_matrix_right(*args):
    q = args[0] if hasattr(args[0], "__len__")  else args
    q0 = q[0]
    q1 = q[1]
    q2 = q[2]
    q3 = q[3]
    return np.array([[q0,-q1,-q2,-q3], [q1,q0,q3,-q2], [q2,-q3,q0,q1], [q3,q2,-q1,q0]])

def scalar_last(p):
    return np.array([p[1], p[2], p[3], p[0]])

def scalar_first(p):
    return np.array([p[3], p[0], p[1], p[2]])

def get_scipy_rotation(p):
    from scipy.spatial.transform import Rotation as R
    r = R.from_quat(scalar_last(p)) # Note the real part comes last for scipy quaternions
    return r

def rotate(q, p):
    """
    rotates 3D vector p using quaternion q
    """
    P=product_matrix_left(q) # q left multiplies 
    Q=product_matrix_right([q[0],-q[1],-q[2],-q[3]]) # q* right multiplies
    #return Q @ P
    out = Q @ P @ np.insert(p,0,0)
    return out[1:]

def rotate_timeseries(q,x):
    """
    rotates each 3D vector data in the timeseries 2D numpy array x, using quaternion q
    """
    out = x.copy()
    for n in range(0,x.shape[0]):
        out[n,1:] = rotate(q,x[n,1:])
    return out

def read_csv(path):
    with open(path) as f:
        first_line = f.readline()
    regex = re.compile('time', re.IGNORECASE)
    if (regex.search(first_line)):
        header=0
    else:
        header=None
    g = pd.read_csv(path, header=header, sep="[;,]", engine='python').to_numpy()
    return g

def delta_degrees(angle0, angle1, isBidirectional=False):
    return delta_angle(angle0, angle1, 360.0, isBidirectional)

def delta_radians(angle0, angle1, isBidirectional=False):
    return delta_angle(angle0, angle1, 2*math.pi, isBidirectional)

def delta_angle(angle0, angle1, full_turn, isBidirectional=False):
    delta = angle1 - angle0
    half_turn = full_turn / 2.0
    if (delta > half_turn):
        delta -= full_turn
    if (delta < -half_turn):
        delta += full_turn
    if (isBidirectional):
        if (delta < -full_turn/4):
            delta += half_turn
        if (delta > full_turn/4):
            delta -= half_turn
    return delta

# Extracts speed and track from DC format gps csv row, converting speed to m/s and track to radians
def speed_track_from_gps_csv(g):
    t=g[0]
    speed = g[3]/3.6
    track = g[4]*math.pi/180
    return np.array([t, speed, track])

# Applies speed_track_from_gps_csv on every row of g, returning a speed track array (in m/s, radians)
def speed_track_from_gpss_csv(g):
    out = []
    for n in range(0,g.shape[0]):
        out.append(speed_track_from_gps_csv(g[n,:]))
    return np.array(out)

def accel_from_speed_track(st1, st2):
    dt = (st2[0] - st1[0])/1000.0 # delta time in s (seconds)
    speed2 = st2[1] # st units: m/s for speed, radians for track
    speed1 = st1[1]
    ax = (speed2 - speed1)/dt
    #s = speed2 * dt # implicit in the following - see math notes: "Speed,track to ax,ay accel"
    theta = -delta_radians(st1[2], st2[2]) # theta_n = -track_n (opposite rotation sense), so delta_theta = - delta_track
    ac = speed2 * theta / dt
    return np.array([st2[0], ax, ac])

def accel_from_speed_tracks(sts):
    out = []
    for n in range(1, sts.shape[0]):
        out.append(accel_from_speed_track(sts[n-1,:], sts[n,:]))
    return np.array(out)

def accels_from_gpss(g):
    sts=speed_track_from_gpss_csv(g)
    return accel_from_speed_tracks(sts)

# Tidy up xi, yi initial conditions
def ba_filter(b,a, x, xi=0, yi=None):
    if (yi is None):
        yi = xi
    if (not hasattr(xi,"__len__")):
        xi = np.ones(len(a) - 0) * xi
    if (not hasattr(yi,"__len__")):
        yi = np.ones(len(b) - 1) * yi       
    zi = signal.lfiltic(b, a, y=yi,x=xi)
    y,zf = signal.lfilter(b,a,x,zi=zi)
    return y

def plot_fullsize():
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()

def add_legend_picker(ax, init_vis=False):
    # Set up a dict mapping legend line to orig line, and enable picking (toggle line visibility) on the legend line
    # https://matplotlib.org/examples/event_handling/legend_picking.html
    fig = ax.figure
    leg = ax.legend()
    leg.get_frame().set_alpha(0.4)
    lined = dict()
    for legline, origline in zip(leg.get_lines(), ax.lines):
        legline.set_picker(5)  # Enables picking, with 5 pts tolerance, on the legline (artist)
        lined[legline] = origline
        origline.set_visible(init_vis)
        if init_vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
    def onpick(event):
        # on the pick event, find the orig line corresponding to the legend proxy line, and toggle the visibility
        legline = event.artist
        #print("legline=",legline)
        origline = lined[legline]
        vis = not origline.get_visible()
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()
    fig.canvas.mpl_connect('pick_event', onpick)

def plot_faccel_gpsaccel(dir, date, q=[], showPlot=True, t0MSin=-1, fig=-1, host=-1):
    """
    """
    dir = dir + ('/' if dir[-1] !='/' else '')
    clrs=plt.rcParams['axes.prop_cycle'].by_key()['color']
    if (fig == -1):
        fig, host = plt.subplots()
    ax=host
    msecToTimeUnit=1.0/1000.0 # time unit seconds
    t0MS = t0MSin
    if (t0MSin == -1):
        t0MS=0
    ax.set_xlabel('seconds');
    host.grid()
    axes=[host];
    lines=[]

    accel=read_csv(dir + 'accel.' + date + '.csv')
    b17,a17=signal.butter(4, 1/17, 'low', analog=False);
    t = (accel[:,0] - t0MS) * msecToTimeUnit
    faccel=np.zeros(accel.shape)
    faccel[:,0] = accel[:,0] # copy over time
    for n in range(1,4):
        faccel[:,n]=ba_filter(b17,a17, accel[:,n])
    lines.append(ax.plot(t, faccel[:,1], label='x f_accel', color=clrs[0])[0]);
    lines.append(ax.plot(t, faccel[:,2], label='y f_accel', color=clrs[1])[0]);
    lines.append(ax.plot(t, accel[:,1], label='x accel', color=clrs[4])[0]);
    lines.append(ax.plot(t, accel[:,2], label='y accel', color=clrs[5])[0]);
    
    if (len(q) == 4):
        ar = rotate_timeseries(q,faccel)
        lines.append(ax.plot(t, ar[:,1], label='x accel rotated', color=clrs[6])[0]);
        lines.append(ax.plot(t, ar[:,2], label='y accel rotated', color=clrs[7])[0]);
    
    gps=read_csv(dir+'gps.'+date+'.csv') # ms,lat,lng,kmph,track,satellites,alt
    gpsAccel = accels_from_gpss(gps)
    t = (gpsAccel[:,0] - t0MS) * msecToTimeUnit
    lines.append(ax.plot(t, gpsAccel[:,1], label='gps x accel', color=clrs[2])[0]);
    lines.append(ax.plot(t, gpsAccel[:,2], label='gps y accel', color=clrs[3], marker='x')[0]);

    ax.set_ylabel('m/s^2')

    host.legend(lines, [l.get_label() for l in lines])
    add_legend_picker(ax, True)
    ax.grid(which='major', color='b', linestyle='-'); 
    if (showPlot):
        plot_fullsize();
        plt.show();
    return t0MS

class IIRFilter:
    def __init__(self, b, a):
        if len(b) == 0 or len(a) == 0:
            raise ValueError("Filter coefficients must not be empty")
        if len(b) != len(a):
            raise ValueError("Filter coefficients must have the same length")

        self.b = b
        self.a = a
        self.input_buffer = [0.0] * len(b)
        self.output_buffer = [0.0] * (len(a) - 1)

    def filter(self, sample):
        self.input_buffer[0] = sample
        output = 0.0

        for i in range(len(self.b)):
            output += self.b[i] * self.input_buffer[i]
            if i > 0:
                output -= self.a[i] * self.output_buffer[i - 1]

        for i in range(len(self.input_buffer) - 1, 0, -1):
            self.input_buffer[i] = self.input_buffer[i - 1]
        for i in range(len(self.output_buffer) - 1, 0, -1):
            self.output_buffer[i] = self.output_buffer[i - 1]

        self.output_buffer[0] = output

        return output

    def get_last_output(self):
        return self.output_buffer[0]

def filter(b,a,input):
    f=IIRFilter(b,a)
    out=[]
    for n in range(len(input)):
        out.append(f.filter(input[n]))
    return out

def test_IIRfilter():
    b,a=signal.butter(4, 1/17, 'low', analog=False);
    f=IIRFilter(b,a)
    x=[0.0]*100; x[0]=1.0
    out=[]
    for n in range(len(x)):
        out.append(f.filter(x[n]))
    expected=signal.lfilter(b,a,x)
    err = expected - out
    sse = err @ err
    thresh = np.finfo(float).eps * len(x)
    assert(sse < thresh)

class IIRFilter3D:
    def __init__(self, b, a):
        self.xf = IIRFilter(b,a)
        self.yf = IIRFilter(b,a)
        self.zf = IIRFilter(b,a)

    def filter(self, v):
        return [self.xf.filter(v[0]), self.yf.filter(v[0]), self.zf.filter(v[2])]

    def get_last_output(self):
        return [self.xf.get_last_output(), self.yf.get_last_output(), self.zf.get_last_output()]


class FilteredOptQ:
    def __init__(self, b, a):
        if len(b) == 0 or len(a) == 0:
            raise ValueError("Filter coefficients must not be empty")
        if len(b) != len(a):
            raise ValueError("Filter coefficients must have the same length")

        self.a_filt = IIRFilter3D(b,a)
        self.ga_filt = IIRFilter3D(b,a)
    
    def update(self, a, ga):
        self.a_filt.filter(a)
        self.ga_filt.filter(ga)
    
    def get_opt_q(self):
        #print(self.a_filt.get_last_output())
        #print(self.ga_filt.get_last_output())
        return get_opt_q_for_v1_to_v2(self.a_filt.get_last_output(), self.ga_filt.get_last_output())

def degrees(q1,q2):
    return np.arccos(q1 @ q2) * 180 / math.pi

def get_opt_q_for_v1_to_v2(a,ga):
    P=product_matrix_right(0,a[0],a[1],a[2])
    Q=product_matrix_left(0,ga[0],ga[1],ga[2])
    M=P.transpose() @ Q
    vals, vecs =np.linalg.eig(M)
    i = np.argmax(vals)
    q = vecs[:,i]
    print(M)
    print("eigenvalues=", vals, ", argmax=",i, ", q=",q, ", angle=", np.arccos(q[0]) * 180/math.pi, "degrees")
    return q,M

def time_slice(x, min_sec, max_sec):
    idxs = np.where((min_sec*1000 <= x[:,0]) & (x[:,0] < max_sec*1000))[0]
    return idxs
    #return slice(start_stop)

def set_fixed_prec_format(n=2):
    format_str = f"%5.{n}f"
    float_formatter = lambda x: format_str % x
    np.set_printoptions(formatter={'float_kind':float_formatter})

def get_filtered_accel_gps_file(dir_in, date):
    dir = dir_in + ('/' if dir_in[-1] !='/' else '')
    accel=read_csv(dir + 'accel.' + date + '.csv')
    b17,a17=signal.butter(4, 1/17, 'low', analog=False);
    faccel=np.zeros(accel.shape)
    faccel[:,0] = accel[:,0] # copy over time
    for n in range(1,4):
        faccel[:,n]=ba_filter(b17,a17, accel[:,n])
    gps=read_csv(dir+'gps.'+date+'.csv') # ms,lat,lng,kmph,track,satellites,alt
    return faccel,gps

def get_opt_q_file(dir_in, date, spd_thresh=7):
    """
    Caclulates the quaterion that rotates the acceleration data to "best" match the GPS data. This is a measure of the device orientation relative to the vehicles axes
    """
    faccel,gps = get_filtered_accel_gps_file(dir_in, date)
    return get_opt_q(faccel, gps, spd_thresh)

def get_opt_q(faccel, gps, spd_thresh=7, print_diag=False):
    t_accel = faccel[:,0]
    gpsAccel = accels_from_gpss(gps)
    M=np.zeros((4,4))
    num_pts_used = 0
    for n in range(0,gpsAccel.shape[0]):
        a_idx = np.argmax(t_accel > gpsAccel[n,0]) - 1
        a = faccel[a_idx,1:]
        ga = np.append(gpsAccel[n,1:], 9.81) # Assume z acceleration is as if vehicle is on a flat road (no slope, nor change in altitude).
        spd = (gps[n,3] + gps[n+1,3])/2
        if (spd < spd_thresh or np.isnan(a).any() or np.isnan(ga).any()):
            continue
        P=product_matrix_right(0,a[0],a[1],a[2])
        Q=product_matrix_left(0,ga[0],ga[1],ga[2])
        M = M + P.transpose() @ Q
        num_pts_used = num_pts_used + 1
    vals, vecs =np.linalg.eig(M)
    i=np.argmax(vals)
    q=vecs[:,i]
    if (print_diag):
        print("eigenvalues=", vals, ", argmax=",i, ", num_pts_used=", num_pts_used)
        print("q=",q, "angle=", np.arccos(q[0]) * 180/math.pi, "degrees")
    return q

