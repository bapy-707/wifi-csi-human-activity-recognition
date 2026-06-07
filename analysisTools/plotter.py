import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import Slider
from matplotlib.widgets import Button
from dataclasses import dataclass
##########################################
@dataclass
class GUI:
    fig: object
    ax: object
    radio: object
    play_button: object
    packet_slider: object
    subcarrier_slider: object
##########################################
def create_play_button(fig):
    ax = fig.add_axes([0.03, 0.03, 0.12, 0.05])
    btn = Button(ax,"Pause")
    return btn
##########################################
def create_packet_slider(fig,num_packets):
    slider_ax = fig.add_axes([0.28, 0.05, 0.60, 0.03])
    slider = Slider(slider_ax,"Packets",0,num_packets - 1,valinit=0,valstep=1)
    return slider
##########################################
def create_subcarrier_slider(fig,num_subcarriers):
    slider_ax = fig.add_axes([0.28, 0.01, 0.60, 0.03])
    slider = Slider(slider_ax,"Subcarrier",0,num_subcarriers - 1, valinit=min(20,num_subcarriers - 1),valstep=1)
    return slider
##########################################
def create_radio_buttons(fig):
    modes = [
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

    rax = fig.add_axes([0.02, 0.30, 0.20, 0.60])
    radio = RadioButtons(rax,modes)
    return radio
##########################################
def create_gui(state, features):
    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_axes([0.28, 0.125, 0.68, 0.82])
    radio = create_radio_buttons(fig)
    play_button = create_play_button(fig)
    packet_slider = create_packet_slider(fig,features["MAG"].shape[0])
    subcarrier_slider = create_subcarrier_slider(fig,features["MAG"].shape[1])
    return GUI(
        fig=fig,
        ax=ax,
        radio=radio,
        play_button=play_button,
        packet_slider=packet_slider,
        subcarrier_slider=subcarrier_slider
    )
##########################################
def draw_iq(ax,I,Q,idx,progress):
    ax.scatter(I, Q)
    ax.set_title(f"IQ Packet {idx} " f"[{progress:.1f}%]")
    ax.set_xlabel("I")
    ax.set_ylabel("Q")
    ax.set_xlim(-128, 128)
    ax.set_ylim(-128, 128)
    ax.grid(True)
##########################################
def draw_magnitude(ax,mag,idx,progress):
    ax.plot(mag)
    ax.set_title(f"Magnitude Packet {idx} "f"[{progress:.1f}%]")
    ax.grid(True)
##########################################
def draw_phase(ax,phase,idx,progress):
    ax.plot(phase)
    ax.set_title(f"Phase Packet {idx} " f"[{progress:.1f}%]")
    ax.grid(True)
##########################################
def draw_magnitude_heatmap(ax,MAG,idx):
    start = max(0,idx - 200)
    ax.imshow(MAG[start:idx+1].T,aspect="auto",origin="lower")
    ax.set_title("Magnitude Heatmap")
##########################################
def draw_motion_metric(ax,metric,idx):
    ax.plot(metric)
    ax.axvline(idx)
    ax.set_title("Motion Metric")
    ax.grid(True)
##########################################
def draw_pca(ax,pca_comp,idx):
    ax.plot(pca_comp[:, 0])
    ax.axvline(idx)
    ax.set_title("PCA Component 1")
    ax.grid(True)
##########################################
def draw_spectrogram(ax,signal,fs):
    import numpy as np
    from scipy.signal import spectrogram
    signal = (signal- np.mean(signal))
    nperseg = min(64,len(signal))
    noverlap = min(48,nperseg - 1)
    f, t, Sxx = spectrogram(signal,fs=fs,nperseg=nperseg,noverlap=noverlap)
    ax.pcolormesh(t,f,10*np.log10(Sxx + 1e-12),shading="auto")
    ax.set_title("Doppler Spectrogram")
##########################################
def draw_waterfall3d(ax,MAG,idx):
    import numpy as np
    start = max(0,idx - 50)
    X, Y = np.meshgrid( np.arange( start,idx + 1), np.arange(MAG.shape[1]))
    Z = MAG[start:idx+1].T
    ax.plot_surface(X,Y,Z)
    ax.set_title("3D Waterfall")
##########################################
def update(frame, state, features, gui):
    if state.playing:
        state.current_packet = (state.current_packet + 1) % features["MAG"].shape[0]
    idx = state.current_packet
    progress = (100.0 * idx /max(1, features["MAG"].shape[0] - 1))
    gui.ax.clear()
    mode = state.current_mode
    if mode == "IQ":
        draw_iq(gui.ax,features["H"][idx].real,features["H"][idx].imag,idx,progress)
    elif mode == "Magnitude":
        draw_magnitude(gui.ax,features["MAG"][idx],idx,progress)
    elif mode == "Phase":
        draw_phase(gui.ax,features["PHASE"][idx],idx,progress)
    elif mode == "MagnitudeHeatmap":
        draw_magnitude_heatmap(gui.ax,features["MAG"],idx)
    elif mode == "MotionMetric":
        draw_motion_metric(gui.ax,features["motion_metric"],min(idx,len(features["motion_metric"]) - 1))
    elif mode == "PCA1":
        draw_pca(gui.ax,features["pca"],idx)
    elif mode == "DopplerSpectrogram":
        draw_spectrogram(gui.ax,features["MAG"][:, state.current_sc],state.fs)
    elif mode == "Velocity":
        vel = estimate_velocity(features["PHASE"],state.current_sc,state.fs)
        gui.ax.text(0.2,0.5,f"{vel:.3f} m/s",fontsize=24)
        gui.ax.axis("off")
    gui.fig.canvas.draw_idle()
##########################################