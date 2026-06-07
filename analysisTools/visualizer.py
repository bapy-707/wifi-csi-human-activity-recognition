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

def packet_progress(idx,total):
    return (100.0 * idx / max(1,total - 1))


def parse_args():
    parser = argparse.ArgumentParser(description="ESP32 CSI Visualizer")
    parser.add_argument("filename",help="CSI file")
    parser.add_argument("--fs",type=float,default=100.0,help="Sampling frequency (Pkts/Sec)")
    parser.add_argument("--interval",type=int,default=50,help="Animation interval (ms)")
    return parser.parse_args()


def main():
    args = parse_args()
    csi = load_csi(args.filename)
    print(csi)
    features = compute_features(*csi)
    state = ViewerState()
    gui = create_gui(state, features)
    anim = FuncAnimation(gui.fig,lambda frame: update(frame,state,features,gui),interval=args.interval,cache_frame_data=False)
    gui.anim = anim
    plt.show()
    
if __name__ == "__main__":
    main()