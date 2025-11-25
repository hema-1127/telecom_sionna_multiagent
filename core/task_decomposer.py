"""
Drop your existing TaskDecomposer here.
Must implement:
  classify(prompt) -> str task_type
  extract_params(prompt, task_type) -> dict
"""
import re

class TaskDecomposer:
    def classify(self, prompt: str) -> str:
        p = prompt.lower()
        if "constellation" in p or "qam" in p or "qpsk" in p:
            return "constellation"
        if "ber" in p or "bit error" in p:
            return "ber"
        if "mimo" in p or "antenna" in p:
            return "mimo_comparison"
        if "radio map" in p or "coverage" in p:
            return "radiomap"
        if "multi" in p and "transmitter" in p:
            return "multi_radio_map"
        return "ber"

    def extract_params(self, prompt: str, task_type: str) -> dict:
        p = prompt.lower()
        params = {}

        # ---- modulation ----
        if "qpsk" in p:
            params["modulation"] = "qpsk"
        else:
            m = re.search(r"(\d+)\s*-\s*qam|(\d+)\s*qam", p)
            if m:
                val = m.group(1) or m.group(2)
                params["modulation"] = f"{val}qam"

        # ---- SNR ----
        snr_vals = re.findall(r"snr\s*=?\s*(-?\d+\.?\d*)", p)
        if snr_vals:
            # if only one value, use snr_db
            if len(snr_vals) == 1:
                params["snr_db"] = float(snr_vals[0])
            else:
                params["snr_db_list"] = [float(x) for x in snr_vals]

        # ---- SNR range like "-5 to 15" ----
        rng = re.search(r"(-?\d+)\s*(to|-)\s*(-?\d+)\s*d?b", p)
        if rng and task_type in ["ber", "mimo_comparison"]:
            start = int(rng.group(1))
            end = int(rng.group(3))
            step = 5
            params["snr_db_list"] = list(range(start, end + 1, step))

        # ---- channel ----
        if task_type == "ber":
            if "rayleigh" in p or "fading" in p:
                params["channel"] = "rayleigh"
            else:
                params["channel"] = "awgn"

        # ---- MIMO configs ----
        if task_type == "mimo_comparison":
            # detect patterns like 1x1, 4x4
            cfgs = re.findall(r"(\d+)\s*x\s*(\d+)", p)
            if cfgs:
                params["configs"] = [{"nt": int(a), "nr": int(b)} for a,b in cfgs]
            else:
                params["configs"] = [{"nt": 1, "nr": 1}, {"nt": 4, "nr": 4}]

        return params
