import os
import numpy as np
import matplotlib.pyplot as plt
from core.sionna_compat import phy_imports

def simulate_ber(
    modulation: str = "qpsk",
    channel: str = "awgn",          # "awgn" or "rayleigh"
    snr_db_list=None,              # e.g. [-5,0,5,10,15]
    n_bits: int = 200000,
    batch_size: int = 2000,
    out_dir: str = "outputs"
):
    os.makedirs(out_dir, exist_ok=True)
    if snr_db_list is None:
        snr_db_list = [-5, 0, 5, 10, 15]

    try:
        import tensorflow as tf
        # Only need Mapper/Demapper/AWGN/FlatFading/ebnodb2no
        _, Mapper, Demapper, AWGN, FlatFadingChannel, ebnodb2no = phy_imports()
    except Exception as e:
        return {"plots": [], "kpis": {}, "error": f"Sionna/TensorFlow import failed: {e}"}

    mod = modulation.lower()

    # bits per symbol k
    if mod == "qpsk":
        k = 2
    elif "qam" in mod:
        M = int(mod.replace("qam", ""))
        k = int(np.log2(M))
    else:
        return {"plots": [], "kpis": {}, "error": f"Unknown modulation: {modulation}"}

    mapper = Mapper(constellation_type="qam", num_bits_per_symbol=k)
    demapper = Demapper("app", constellation_type="qam", num_bits_per_symbol=k)

    fading = (channel.lower() == "rayleigh")
    if fading:
        ch = FlatFadingChannel(num_tx_ant=1, num_rx_ant=1, add_awgn=True)
    else:
        ch = AWGN()

    bers = []

    for snr_db in snr_db_list:
        no = ebnodb2no(snr_db, k, coderate=1.0)

        n_err = 0
        n_tot = 0

        while n_tot < n_bits:
            b = tf.random.uniform([batch_size, k], 0, 2, dtype=tf.int32)
            x = mapper(b)

            if fading:
                # Sionna 1.x style
                try:
                    y, h = ch(x, no)
                except TypeError:
                    # old fallback
                    y, h = ch([x, no])
                llr = demapper(y, h, no) if hasattr(demapper, "__call__") else demapper([y, h, no])
            else:
                try:
                    y = ch(x, no)
                except TypeError:
                    y = ch([x, no])
                llr = demapper(y, no) if hasattr(demapper, "__call__") else demapper([y, no])

            b_hat = tf.cast(llr > 0, tf.int32)
            n_err += tf.reduce_sum(tf.cast(tf.not_equal(b, b_hat), tf.int32)).numpy()
            n_tot += batch_size * k

        bers.append(n_err / n_tot)

    # Plot
    fig = plt.figure()
    plt.semilogy(snr_db_list, bers, marker="o")
    plt.title(f"BER vs SNR ({modulation.upper()} - {channel.upper()})")
    plt.xlabel("SNR (dB)")
    plt.ylabel("BER")
    plt.grid(True, which="both")

    plot_path = os.path.join(out_dir, f"ber_{mod}_{channel}.png")
    plt.savefig(plot_path, bbox_inches="tight")
    plt.close(fig)

    return {
        "plots": [plot_path],
        "kpis": {
            "snr_db": snr_db_list,
            "ber": bers,
            "modulation": modulation,
            "channel": channel
        }
    }
