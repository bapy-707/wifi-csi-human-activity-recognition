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
from dataclasses import dataclass


from fileLoader import *
from featureExtraction import *
from plotter import *

@dataclass
class ViewerState:
    current_mode: str = "IQ"
    current_sc: int = 0
    current_packet: int = 0
    playing: bool = True
    fs: float = 100.0
################################################
def packet_progress(idx,total):
    return (100.0 * idx / max(1,total - 1))
################################################
def parse_args():
    parser = argparse.ArgumentParser(description="ESP32 CSI Visualizer")
    parser.add_argument("filename",help="CSI file")
    parser.add_argument("--fs",type=float,default=100.0,help="Sampling frequency (Pkts/Sec)")
    parser.add_argument("--interval",type=int,default=50,help="Animation interval (ms)")
    return parser.parse_args()
################################################
def normalize_axis(features):
    features["phase_min"] = np.min(features["PHASE"])
    features["phase_max"] = np.max(features["PHASE"])
    features["pca"] = compute_pca(features["MAG"])
    features["mag_min"] = np.min(features["MAG"])
    features["mag_max"] = np.max(features["MAG"])
    features["motion_max"] = np.max(features["motion_metric"])
    features["pca_min"] = np.min(features["pca"][:,0])
    features["pca_max"] = np.max(features["pca"][:,0])
    return(features)
################################################
def main():
    args = parse_args()
    csi = load_csi(args.filename)
    #print(csi)
    features = compute_features(*csi)
    features=normalize_axis(features)
    print(features["MAG"])

    state = ViewerState(current_mode="IQ",current_sc=min(20,features["MAG"].shape[1] - 1),current_packet=0,playing=True,fs=args.fs)
    gui = create_gui(state, features)

    # Connect buttons with actions
    gui.radio.on_clicked(lambda label:setattr(state,"current_mode",label))
    gui.subcarrier_slider.on_changed(lambda val:setattr(state,"current_sc",int(val)))
    gui.packet_slider.on_changed(lambda val: setattr(state, "current_packet", int(val)))
    gui.play_button.on_clicked(lambda event: (setattr(state, "playing", not state.playing), gui.play_button.label.set_text("Pause" if state.playing else "Play")))
    print(f"Mode={state.current_mode}, Packet={state.current_packet}, SC={state.current_sc}")

    anim = FuncAnimation(gui.fig,lambda frame: update(frame,state,features,gui),interval=args.interval,cache_frame_data=False)
    gui.anim = anim
    plt.show()
################################################
if __name__ == "__main__":
    main()