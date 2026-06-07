"""
ESP32 CSI Visualizer
- Input File format `label,I₀,Q₀,I₁,Q₁,...,Iₙ,Qₙ`
- python3 csi_visualizer.py ../Data/csi_com3.csv
- python3 csi_visualizer.py ../Data/csi_com3.csv --interval 500 # For reduced animation speed
- python3 csi_visualizer.py ../Data/csi_com3.csv --fs 100 # required for Doppler spectrogram. Means 100 Pkts/Sec.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import RadioButtons, Button, Slider
from scipy.signal import spectrogram
from sklearn.decomposition import PCA




parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("--fs", type=float, default=100.0)
parser.add_argument("--interval", type=int, default=50)
args = parser.parse_args()

I_all, Q_all = [], []

with open(args.filename, "r", errors="ignore") as f:
    for line in f:
        p = line.strip().split(",")
        if len(p) < 3:
            continue
        try:
            vals = np.array(list(map(int, p[1:])))
        except:
            continue

        if len(vals) % 2:
            vals = vals[:-1]

        I_all.append(vals[0::2])
        Q_all.append(vals[1::2])

min_sc = min(len(x) for x in I_all)

I_all = np.array([x[:min_sc] for x in I_all])
Q_all = np.array([x[:min_sc] for x in Q_all])

H = I_all + 1j * Q_all
MAG = np.abs(H)
PHASE = np.angle(H)
UPHASE = np.unwrap(PHASE, axis=1)

NUM_PACKETS, NUM_SC = MAG.shape

motion_metric = np.mean(np.abs(np.diff(MAG, axis=0)), axis=1)
energy_metric = np.sum(MAG**2, axis=1)

try:
    pca_comp = PCA(n_components=3).fit_transform(MAG)
except:
    pca_comp = np.zeros((NUM_PACKETS, 3))

MODES = [
    "IQ",
    "Magnitude",
    "Phase",
    "MagnitudeHeatmap",
    "MotionMetric",
    "PCA1",
    "DopplerSpectrogram",
    "Velocity",
    "Waterfall3D"
]

current_mode = MODES[0]
current_sc = min(20, NUM_SC - 1)
playing = True

fig = plt.figure(figsize=(14, 9))

ax = fig.add_axes([0.28, 0.10, 0.68, 0.82])

rax = fig.add_axes([0.02, 0.30, 0.20, 0.60])
radio = RadioButtons(rax, MODES)

play_ax = fig.add_axes([0.03, 0.20, 0.12, 0.05])
play_button = Button(play_ax, "Pause")

slider_ax = fig.add_axes([0.28, 0.03, 0.60, 0.03])
slider = Slider(
    slider_ax,
    "Subcarrier",
    0,
    NUM_SC - 1,
    valinit=current_sc,
    valstep=1
)

def mode_change(label):
    global current_mode
    current_mode = label

radio.on_clicked(mode_change)

def slider_change(val):
    global current_sc
    current_sc = int(val)

slider.on_changed(slider_change)

def toggle(event):
    global playing
    playing = not playing
    play_button.label.set_text("Pause" if playing else "Play")

play_button.on_clicked(toggle)

def estimate_velocity():
    phase_ts = np.unwrap(PHASE[:, current_sc])
    dphase = np.diff(phase_ts)

    fd = np.median(dphase) * args.fs / (2 * np.pi)

    fc = 2.437e9
    c = 3e8

    velocity = fd * c / fc
    return velocity

frame_counter = [0]

def update(frame):

    if playing:
        frame_counter[0] = (frame_counter[0] + 1) % NUM_PACKETS

    idx = frame_counter[0]

    global ax

    if current_mode == "Waterfall3D":
        fig.delaxes(ax)
        ax_new = fig.add_axes([0.28, 0.10, 0.68, 0.82], projection="3d")
        ax = ax_new

        start = max(0, idx - 50)

        X, Y = np.meshgrid(
            np.arange(start, idx + 1),
            np.arange(NUM_SC)
        )

        Z = MAG[start:idx + 1].T

        ax.plot_surface(X, Y, Z)

        ax.set_title("3D Waterfall")

    else:

        if hasattr(ax, "zaxis"):
            fig.delaxes(ax)
            ax_new = fig.add_axes([0.28, 0.10, 0.68, 0.82])
            ax = ax_new

        ax.clear()

        if current_mode == "IQ":
            ax.scatter(I_all[idx], Q_all[idx])
            ax.set_title(f"IQ Packet {idx}")

        elif current_mode == "Magnitude":
            ax.plot(MAG[idx])
            ax.set_title(f"Magnitude Packet {idx}")

        elif current_mode == "Phase":
            ax.plot(PHASE[idx])
            ax.set_title(f"Phase Packet {idx}")

        elif current_mode == "MagnitudeHeatmap":
            start = max(0, idx - 200)
            ax.imshow(
                MAG[start:idx+1].T,
                aspect="auto",
                origin="lower"
            )
            ax.set_title("Magnitude Heatmap")

        elif current_mode == "MotionMetric":
            ax.plot(motion_metric)
            ax.axvline(idx)
            ax.set_title("Motion Metric")

        elif current_mode == "PCA1":
            ax.plot(pca_comp[:,0])
            ax.axvline(idx)
            ax.set_title("PCA Component 1")

        elif current_mode == "DopplerSpectrogram":

            signal = MAG[:, current_sc]
            signal = signal - np.mean(signal)

            nperseg = min(64, len(signal))
            noverlap = min(48, nperseg - 1)

            f, t, Sxx = spectrogram(
                signal,
                fs=args.fs,
                nperseg=nperseg,
                noverlap=noverlap
            )

            ax.pcolormesh(
                t,
                f,
                10*np.log10(Sxx + 1e-12),
                shading="auto"
            )

            ax.set_title(
                f"Spectrogram SC={current_sc}"
            )

        elif current_mode == "Velocity":

            vel = estimate_velocity()

            ax.text(
                0.2,
                0.5,
                f"Estimated Velocity\n{vel:.3f} m/s",
                fontsize=24
            )

            ax.set_title(
                f"Relative Doppler Velocity SC={current_sc}"
            )
            ax.axis("off")

        ax.grid(True)

ani = FuncAnimation(
    fig,
    update,
    interval=args.interval,
    cache_frame_data=False
)

plt.show()
