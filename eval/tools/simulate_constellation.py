import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from core.sionna_compat import phy_imports


def simulate_constellation(
    modulation: str = "16qam",
    snr_db: float = 15.0,
    n_symbols: int = 2000,
    out_dir: str = "outputs"
):
    os.makedirs(out_dir, exist_ok=True)

    try:
        import tensorflow as tf
        _, Mapper, _, AWGN, _, _ = phy_imports()
    except Exception as e:
        return {"plots": [], "kpis": {}, "error": f"Sionna/TensorFlow import failed: {e}"}

    mod = modulation.lower()

    # ---- bits per symbol ----
    if mod == "qpsk":
        k = 2                      # log2(4)
        M = 4
    elif "qam" in mod:
        M = int(mod.replace("qam", ""))
        k = int(np.log2(M))
    else:
        return {"plots": [], "kpis": {}, "error": f"Unknown modulation: {modulation}"}

    # Sionna 1.x way: no Constellation object needed
    mapper = Mapper(constellation_type="qam", num_bits_per_symbol=k)
    awgn = AWGN()

    # Random bits -> symbols
    bits = tf.random.uniform([n_symbols, k], 0, 2, dtype=tf.int32)
    x = mapper(bits)

    # Noise variance
    snr_lin = 10 ** (snr_db / 10)
    noise_var = 1.0 / snr_lin

    #  AWGN call differs between 1.x and 0.x -> support both
    try:
        y = awgn(x, tf.constant(noise_var, tf.float32))     # Sionna 1.x style :contentReference[oaicite:1]{index=1}
    except TypeError:
        y = awgn([x, tf.constant(noise_var, tf.float32)])   # Sionna 0.x fallback

    y_np = y.numpy().reshape(-1)

    # Plot
    fig = plt.figure(figsize=(5, 5))
    plt.scatter(np.real(y_np), np.imag(y_np), s=6, alpha=0.6)
    plt.title(f"{modulation.upper()} Constellation @ {snr_db} dB")
    plt.xlabel("In-phase")
    plt.ylabel("Quadrature")
    plt.grid(True)

    plot_path = os.path.join(out_dir, f"constellation_{mod}_{snr_db}db.png")
    plt.savefig(plot_path, bbox_inches="tight")
    plt.close(fig)

    return {
        "plots": [plot_path],
        "kpis": {"modulation": modulation, "snr_db": snr_db, "n_symbols": n_symbols}
    }
