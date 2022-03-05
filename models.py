from datetime import datetime
from typing import List
import numpy as np


class Observation:
    def __init__(self, observation_primitive):
        self.mrn = str(observation_primitive.mrn)
        self.date = observation_primitive.date.date()
        self.bed = observation_primitive.bed
        self.swabs = []
        self._get_swabs(observation_primitive)

    def _get_swabs(self, observation_primitive):
        for i in range(1, 5):
            swab_date_string = f"swab{i}_date"
            swab_variant_string = f"swab{i}_variant"
            if getattr(observation_primitive, swab_date_string):
                try:
                    date = getattr(observation_primitive, swab_date_string).date()
                    variant = (
                        getattr(observation_primitive, swab_variant_string)
                        .replace(" ", "")
                        .lower()
                    )
                    self.swabs.append({"date": date, "variant": variant})
                except AttributeError:
                    pass


class Patient:
    def __init__(self, mrn: str, swabs: list, date: datetime):
        self.mrn = mrn
        self.swabs = swabs
        self.dates = []
        self._num_observations = None
        self._num_swabs = None
        self._variant = None
        self._estimated_stay = None
        self.add_date(date)

    def add_date(self, date: datetime):
        self.dates.append(date)

    @property
    def num_observations(self):
        if self._num_observations is None:
            self._num_observations = len(self.dates)
        return self._num_observations

    @property
    def num_swabs(self):
        if self._num_swabs is None:
            self._num_swabs = len(self.swabs)
        return self._num_swabs

    @property
    def variant(self):
        if self._variant is None:
            if self.num_swabs > 0:
                self._variant = self.swabs[0]["variant"]
            else:
                self._variant = "no_pcr"
        return self._variant

    @property
    def time_to_neg(self):
        swab_variants = [swab["variant"] for swab in self.swabs]
        if "pcr-ve" in swab_variants:
            if "indeterminate" not in swab_variants:
                first_neg = swab_variants.index("pcr-ve")
                return self.swabs[first_neg]["date"] - self.swabs[0]["date"]
        return

    @property
    def estimated_stay(self):
        if self._estimated_stay is None:
            if self.num_swabs > 0:
                first_swab_date = self.swabs[0]["date"]
                first_observation_date = self.dates[0]
                last_swab_date = self.swabs[-1]["date"]
                last_observation_date = self.dates[-1]
                start_date = (
                    first_swab_date
                    if first_swab_date < first_observation_date
                    else first_observation_date
                )
                end_date = (
                    last_observation_date
                    if last_observation_date > last_swab_date
                    else last_swab_date
                )

                self._estimated_stay = (end_date - start_date).days
            else:
                self._estimated_stay = 0
        return self._estimated_stay


class StayData:
    def __init__(self, stays: List, variant: str, hist_range: int):
        self.variant = variant
        self.hist_range = hist_range
        self.stays = stays
        self.total_patient_stays = np.array(stays).sum()
        self.median_stay = np.median(np.array(stays))

    @property
    def hist(self):
        hist = []
        for stay in range(self.hist_range):
            try:
                hist.append((stay, np.bincount(self.stays)[stay]))
            except Exception:
                hist.append((stay, 0))

        return {
            "stays": np.array([stay for stay, _ in hist]),
            "count": np.array([count for _, count in hist]),
        }
