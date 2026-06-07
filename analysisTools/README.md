# Analysis Tool(s) for Raw CSI Data
### Visualizer
* Install dependencies
```
sudo apt install python3-sklearn
```
* How to Use
    - Input File format `label,I₀,Q₀,I₁,Q₁,...,Iₙ,Qₙ`
    - ```
        - python3 visualizer.py ../Data/csi_com3.csv
        - python3 visualizer.py ../Data/csi_com3.csv --interval 500 # For reduced animation speed
        - python3 visualizer.py ../Data/csi_com3.csv --fs 100 # required for Doppler spectrogram. Means 100 Pkts/Sec.
```
