
def compute_features(I_all, Q_all):
    import numpy as np
    H = I_all + 1j * Q_all
    MAG = np.abs(H)
    PHASE = np.angle(H)
    UPHASE = np.unwrap(PHASE,axis=1)
    motion_metric = np.mean(np.abs(np.diff(MAG, axis=0)),axis=1)
    energy_metric = np.sum(MAG ** 2,axis=1)
    return {
        "H": H,
        "MAG": MAG,
        "PHASE": PHASE,
        "UPHASE": UPHASE,
        "motion_metric": motion_metric,
        "energy_metric": energy_metric
    }
################################################
def compute_pca(MAG):
    import numpy as np
    from sklearn.decomposition import PCA
    try:
        pca = PCA(n_components=3)
        return pca.fit_transform(MAG)
    except Exception:
        return np.zeros((MAG.shape[0], 3))
################################################
def compute_variance_map(MAG,window=20):
    import numpy as np
    result = []
    for i in range(window,len(MAG)):
        result.append(np.var(MAG[i-window:i],axis=0))
    if len(result) == 0:
        return np.zeros((1, MAG.shape[1]))
    return np.array(result)
################################################
def estimate_velocity(phase_matrix,subcarrier,fs):
    import numpy as np
    phase_ts = np.unwrap(phase_matrix[:, subcarrier])
    dphase = np.diff(phase_ts)
    fd = (np.median(dphase)* fs/ (2 * np.pi))
    fc = 2.437e9
    c = 3e8
    velocity = (fd* c/ fc)
    return velocity