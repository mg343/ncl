# figure 8 baseline sim
# bicycle model + pure pursuit steering + PI speed
# run from repo root: python sim/figure8_baseline.py

import numpy as np
import matplotlib.pyplot as plt
import os

A = 2.0       # figure 8 size [m]
NPTS = 2000   # path points

DT = 0.01     # 100 Hz
L = 0.30      # wheelbase [m], PLACEHOLDER - measure on car
TAU = 0.1     # servo lag [s]
MAXSTEER = np.deg2rad(30)
M = 2.5       # mass [kg], PLACEHOLDER
C = 1.0       # drag [N/(m/s)]
MASS_ADDED = 1.0  # [kg] for the mass disturbance test

LOOKAHEAD = 0.5  # [m]
VREF = 1.5       # [m/s]
KP = 4.0
KI = 2.0

NLAPS = 8


def figure8():
    # lemniscate of gerono
    t = np.linspace(0, 2*np.pi, NPTS, endpoint=False)
    px = A*np.sin(t)
    py = A*np.sin(t)*np.cos(t)

    # arc length (wraps around at the end)
    ds = np.sqrt(np.diff(px, append=px[0])**2 + np.diff(py, append=py[0])**2)
    s = np.zeros(NPTS)
    s[1:] = np.cumsum(ds[:-1])
    lap_len = np.sum(ds)

    # tangent
    tx = np.roll(px, -1) - np.roll(px, 1)
    ty = np.roll(py, -1) - np.roll(py, 1)
    nrm = np.sqrt(tx**2 + ty**2)
    tx = tx/nrm
    ty = ty/nrm
    return px, py, tx, ty, s, lap_len


def nearest(x, y, px, py, iprev):
    # only search near the last index, otherwise it jumps to the other branch at the crossover
    # 5 back / 80 ahead seems fine at 1.5 m/s
    idx = np.arange(iprev - 5, iprev + 80) % len(px)
    d = (px[idx] - x)**2 + (py[idx] - y)**2
    return idx[np.argmin(d)]


def signed_cte(x, y, i, px, py, tx, ty):
    # cross product, + = car is left of path
    return tx[i]*(y - py[i]) - ty[i]*(x - px[i])


def run(nlaps=NLAPS, mass_change_lap=None):
    px, py, tx, ty, s, lap_len = figure8()

    # start at index 0 pointing along the path, stopped
    x = px[0]; y = py[0]
    th = np.arctan2(ty[0], tx[0])
    v = 0.0; delta = 0.0
    i = 0
    eint = 0.0
    dist = 0.0
    m = M

    xs, ys, ctes, laps, vs = [], [], [], [], []

    while dist < nlaps*lap_len:
        lap = int(dist/lap_len)
        if mass_change_lap is not None and lap >= mass_change_lap:
            m = M + MASS_ADDED

        i = nearest(x, y, px, py, i)
        e = signed_cte(x, y, i, px, py, tx, ty)

        # pure pursuit - goal pt is LOOKAHEAD ahead along the path (arc length), not euclidean
        ahead = (s - s[i]) % lap_len
        ahead[ahead == 0] = lap_len   # dont want to pick i itself
        ahead[ahead < LOOKAHEAD] = 1e9
        g = np.argmin(ahead)
        alpha = np.arctan2(py[g] - y, px[g] - x) - th
        delta_cmd = np.arctan2(2*L*np.sin(alpha), LOOKAHEAD)
        delta_cmd = np.clip(delta_cmd, -MAXSTEER, MAXSTEER)

        # PI speed
        ev = VREF - v
        eint += ev*DT
        F = KP*ev + KI*eint

        xs.append(x); ys.append(y); ctes.append(e); laps.append(lap); vs.append(v)

        # euler step
        x = x + v*np.cos(th)*DT
        y = y + v*np.sin(th)*DT
        th = th + v/L*np.tan(delta)*DT
        delta = delta + (delta_cmd - delta)/TAU*DT
        v = v + (F - C*v)/m*DT
        dist += v*DT

    return {'x': np.array(xs), 'y': np.array(ys), 'cte': np.array(ctes),
            'lap': np.array(laps), 'v': np.array(vs)}


def lap_rms(log, nlaps=NLAPS):
    rms = []
    for k in range(nlaps):
        e = log['cte'][log['lap'] == k]
        rms.append(np.sqrt(np.mean(e**2)))
    return np.array(rms)


if __name__ == '__main__':
    outdir = os.path.join(os.path.dirname(__file__), 'out')
    os.makedirs(outdir, exist_ok=True)

    px, py, tx, ty, s, lap_len = figure8()
    print('lap length', round(lap_len, 3), 'm')

    log = run()
    rms = lap_rms(log)

    # mass disturbance check - add 1kg from lap 5 (index 4)
    log2 = run(mass_change_lap=4)
    rms2 = lap_rms(log2)

    print('lap  rms [cm]  rms +1kg [cm]')
    for k in range(NLAPS):
        print(k+1, '  ', round(rms[k]*100, 3), '  ', round(rms2[k]*100, 3))
    # print('final speed', log['v'][-1])

    plt.figure(figsize=(8, 5))
    plt.plot(px, py, 'k--', lw=1, label='reference')
    plt.plot(log['x'], log['y'], lw=1, label='car')
    plt.axis('equal')
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.title('figure 8 - pure pursuit baseline')
    plt.legend()
    plt.savefig(os.path.join(outdir, 'baseline_path.png'), dpi=150)

    plt.figure(figsize=(6, 4))
    plt.plot(range(1, NLAPS+1), rms*100, 'o-', label='baseline')
    plt.plot(range(1, NLAPS+1), rms2*100, 's--', label='+1 kg from lap 5')
    plt.ylim(0, 3)
    plt.xlabel('lap')
    plt.ylabel('RMS cross-track error [cm]')
    plt.legend(loc='lower right')
    plt.grid()
    plt.savefig(os.path.join(outdir, 'baseline_lap_error.png'), dpi=150)
    # plt.show()
