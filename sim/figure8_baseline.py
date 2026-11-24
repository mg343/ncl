# figure 8 baseline sim
# car is a 4 wheel diff drive (skid steer), no steering servo
# unicycle model + wheel speed lag, pure pursuit gives turn rate
# run from repo root: python sim/figure8_baseline.py

import numpy as np
import matplotlib.pyplot as plt
import os

A = 2.0       # figure 8 size [m]
NPTS = 2000   # path points

DT = 1/30     # car's control loop runs at 30 Hz
B = 0.24      # wheel separation [m], from old config - MEASURE (comment there said 125mm??)
TAU = 0.15    # wheel speed lag [s], PLACEHOLDER
VMAX = 0.9    # max wheel speed [m/s] (old config)
VMIN = 0.38   # wheels dont move below this (static friction), old config

LOOKAHEAD = 0.5  # [m]
VREF = 0.7       # [m/s], car tops out ~0.9-1.0

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
    idx = np.arange(iprev - 5, iprev + 80) % len(px)
    d = (px[idx] - x)**2 + (py[idx] - y)**2
    return idx[np.argmin(d)]


def signed_cte(x, y, i, px, py, tx, ty):
    # cross product, + = car is left of path
    return tx[i]*(y - py[i]) - ty[i]*(x - px[i])


def run(nlaps=NLAPS):
    px, py, tx, ty, s, lap_len = figure8()

    # start at index 0 pointing along the path, stopped
    x = px[0]; y = py[0]
    th = np.arctan2(ty[0], tx[0])
    vl = 0.0; vr = 0.0   # actual wheel speeds (each side)
    i = 0
    dist = 0.0

    xs, ys, ctes, laps, vs = [], [], [], [], []

    while dist < nlaps*lap_len:
        lap = int(dist/lap_len)

        i = nearest(x, y, px, py, i)
        e = signed_cte(x, y, i, px, py, tx, ty)

        # pure pursuit - goal pt is LOOKAHEAD ahead along the path (arc length), not euclidean
        ahead = (s - s[i]) % lap_len
        ahead[ahead == 0] = lap_len   # dont want to pick i itself
        ahead[ahead < LOOKAHEAD] = 1e9
        g = np.argmin(ahead)
        alpha = np.arctan2(py[g] - y, px[g] - x) - th
        w_cmd = 2*VREF*np.sin(alpha)/LOOKAHEAD   # turn rate = v * curvature

        # diff drive: split into left/right wheel speeds
        vl_cmd = np.clip(VREF - w_cmd*B/2, -VMAX, VMAX)
        vr_cmd = np.clip(VREF + w_cmd*B/2, -VMAX, VMAX)

        v = (vl + vr)/2
        w = (vr - vl)/B
        xs.append(x); ys.append(y); ctes.append(e); laps.append(lap); vs.append(v)

        # euler step
        x = x + v*np.cos(th)*DT
        y = y + v*np.sin(th)*DT
        th = th + w*DT
        vl = vl + (vl_cmd - vl)/TAU*DT
        vr = vr + (vr_cmd - vr)/TAU*DT
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

    print('lap  rms [cm]')
    for k in range(NLAPS):
        print(k+1, '  ', round(rms[k]*100, 3))
    # print('final speed', log['v'][-1])

    plt.figure(figsize=(8, 5))
    plt.plot(px, py, 'k--', lw=1, label='reference')
    plt.plot(log['x'], log['y'], lw=1, label='car')
    plt.axis('equal')
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.title('figure 8 - pure pursuit baseline (diff drive)')
    plt.legend()
    plt.savefig(os.path.join(outdir, 'baseline_path.png'), dpi=150)

    plt.figure(figsize=(6, 4))
    plt.plot(range(1, NLAPS+1), rms*100, 'o-')
    plt.ylim(0, 1.5*max(rms)*100)
    plt.xlabel('lap')
    plt.ylabel('RMS cross-track error [cm]')
    plt.grid()
    plt.savefig(os.path.join(outdir, 'baseline_lap_error.png'), dpi=150)
    # plt.show()
