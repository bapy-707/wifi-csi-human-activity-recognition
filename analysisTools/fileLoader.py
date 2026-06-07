def load_csi(filename):
    import numpy as np
    I_all = []
    Q_all = []
    with open(filename, "r", errors="ignore") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 3:
                continue
            try:
                vals = np.array(list(map(int, parts[1:])))
            except Exception:
                continue
            if len(vals) % 2:
                vals = vals[:-1]
            if len(vals) < 2:
                continue
            I_all.append(vals[0::2])
            Q_all.append(vals[1::2])
    if not I_all:
        raise RuntimeError("No CSI packets found")
    min_sc = min(len(x) for x in I_all)
    I_all = np.array([x[:min_sc] for x in I_all])
    Q_all = np.array([x[:min_sc] for x in Q_all])
    return(I_all, Q_all)