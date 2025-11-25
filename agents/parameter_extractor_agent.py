import re
import logging

class ParameterExtractorAgent:
    """
    Extracts parameters based on task_type.
    Must accept decomposer because main.py passes it.
    """
    def __init__(self, decomposer):
        self.decomposer = decomposer
        self.logger = logging.getLogger("ParameterExtractorAgent")

    def run(self, task_spec):
        prompt = task_spec.raw_prompt.lower()
        params = {}

        # -------------------------
        # CONSTELLATION
        # -------------------------
        if task_spec.task_type == "constellation":
            params["modulation"] = self._extract_modulation(prompt)
            params["snr_db"] = self._extract_snr(prompt, default=10)
            task_spec.parameters = params
            self.logger.info(f"Extracted params: {params}")
            return task_spec

        # -------------------------
        # BER
        # -------------------------
        if task_spec.task_type == "ber":
            params["modulation"] = self._extract_modulation(prompt)
            params["channel"] = self._extract_channel(prompt)
            params["snr_db_list"] = self._extract_snr_list(prompt)
            task_spec.parameters = params
            self.logger.info(f"Extracted params: {params}")
            return task_spec

        # -------------------------
        # MIMO COMPARISON
        # -------------------------
        if task_spec.task_type == "mimo_comparison":
            params["modulation"] = self._extract_modulation(prompt)
            params["snr_db_list"] = self._extract_snr_list(prompt)
            params["configs"] = self._extract_mimo_configs(prompt)
            task_spec.parameters = params
            self.logger.info(f"Extracted params: {params}")
            return task_spec

        # -------------------------
        # SINGLE RADIO MAP
        # -------------------------
        if task_spec.task_type == "radiomap":
            params["tx_pos"] = self._extract_single_tx(prompt)
            task_spec.parameters = params
            self.logger.info(f"Extracted params: {params}")
            return task_spec

        # -------------------------
        # MULTI RADIO MAP
        # -------------------------
        if task_spec.task_type == "multi_radio_map":
            params["tx_positions"] = self._extract_multi_tx(prompt)
            params["combine_mode"] = self._extract_combine_mode(prompt)
            task_spec.parameters = params
            self.logger.info(f"Extracted params: {params}")
            return task_spec

        # fallback
        task_spec.parameters = {}
        self.logger.info("Extracted params: {}")
        return task_spec

    # -------------------------
    # HELPERS
    # -------------------------

    def _extract_modulation(self, text):
        for m in ["qpsk", "16qam", "64qam", "256qam"]:
            if m in text:
                return m
        return "qpsk"

    def _extract_snr(self, text, default=10):
        # matches "snr 15", "snr=15", "snr -5"
        match = re.search(r"snr\s*[=:]?\s*(-?\d+(\.\d+)?)", text)
        if match:
            return float(match.group(1))
        return float(default)

    def _extract_snr_list(self, text):
        # Case 1: "from -5 to 15"
        m = re.search(r"from\s*(-?\d+)\s*to\s*(-?\d+)", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            step = 5 if abs(b-a) >= 10 else 1
            return list(range(a, b + 1, step))

        # Case 2: explicit list like "-5, 0, 5, 10, 15"
        nums = re.findall(r"-?\d+", text)
        nums = [int(n) for n in nums]
        if len(nums) >= 2:
            return nums

        return [-5, 0, 5, 10, 15]

    def _extract_channel(self, text):
        if "rayleigh" in text or "fading" in text:
            return "rayleigh"
        return "awgn"

    def _extract_mimo_configs(self, text):
        configs = []
        matches = re.findall(r"(\d+)\s*x\s*(\d+)", text)
        for nt, nr in matches:
            configs.append({"nt": int(nt), "nr": int(nr)})
        if configs:
            return configs
        return [{"nt": 1, "nr": 1}, {"nt": 4, "nr": 4}]

    def _extract_single_tx(self, text):
        match = re.findall(r"\(([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)", text)
        if match:
            x, y, z = match[0]
            return [float(x), float(y), float(z)]
        return [0, 0, 10]

    def _extract_multi_tx(self, text):
        matches = re.findall(r"\(([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)", text)
        if matches:
            return [[float(a), float(b), float(c)] for (a, b, c) in matches]
        return [[0, 0, 10], [60, 0, 10], [-60, 0, 10]]

    def _extract_combine_mode(self, text):
        if "sum" in text or "adding" in text or "aggregate" in text:
            return "sum"
        return "max"
