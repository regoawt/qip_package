import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from typing import List

from models import Observation, Patient, StayData


def _get_observations(df: pd.DataFrame):
    observations = []
    for i in range(len(df)):
        row = df.iloc[i]
        if str(row.mrn) != "nan":
            observations.append(Observation(row))
    return observations


def get_patients(observations: List[Observation]):
    patients = {}
    for observation in observations:
        if patients.get(observation.mrn, None):
            patient = patients[observation.mrn]
            patient.add_date(observation.date)
        else:
            patient = Patient(
                mrn=observation.mrn, swabs=observation.swabs, date=observation.date
            )
            patients[observation.mrn] = patient
    return list(patients.values())


def get_stay_data(patients: List[Patient], hist_range: int, variant: str = None):
    patient_list = (
        [patient for patient in patients if patient.variant == variant]
        if variant
        else [patient for patient in patients]
    )
    patient_stays = [patient.estimated_stay for patient in patient_list]

    return StayData(patient_stays, variant, hist_range)


def get_variant_data(patients):
    variants = {}
    for patient in patients:
        if patient.variant:
            if variants.get(patient.variant):
                variants[patient.variant].append(patient.num_swabs)
            else:
                variants[patient.variant] = [patient.num_swabs]
    return variants


if __name__ == "__main__":
    data = pd.read_excel("data.xlsx", sheet_name=0)
    patients = get_patients(_get_observations(data))
    total_patients = len(patients)
    variants = get_variant_data(patients)

    max_stay = max([patient.estimated_stay for patient in patients]) + 1
    study_days = sum([patient.num_observations for patient in patients])
    fig, ax = plt.subplots()

    # Patients by variant
    # bottom = np.array([0] * max_stay)
    # for variant in set([patient.variant for patient in patients]):
    #     stay_data = get_stay_data(patients, max_stay, variant)
    #     ax.bar(
    #         stay_data.hist["stays"],
    #         stay_data.hist["count"],
    #         label=stay_data.variant,
    #         bottom=bottom,
    #     )
    #     bottom = bottom + stay_data.hist["count"]

    # All patients
    stay_data = get_stay_data(patients, max_stay+1)
    ax.bar(
        stay_data.hist["stays"],
        stay_data.hist["count"]
    )
    ax.set_xlabel("Stay length")
    ax.set_ylabel("Number of patients")
    ax.legend()
    plt.show()

    # print([patient.time_to_neg for patient in patients if patient.time_to_neg is not None])

    print(f"Total patients: {total_patients}")
    print(
        f"Total patient-days: {get_stay_data(patients, max_stay+1).total_patient_stays}"
    )
    print(f"Study-days: {study_days}")
    print(f"Median stay: {get_stay_data(patients, max_stay+1).median_stay}")
    # print(f"No PCR: {len(no_pcr)}\n")

    print("\t\t\t\tSwab 1 \tSwab 2 \tSwab 3 \tSwab 4")
    for key in variants.keys():
        print(
            f'{key}{"-"*(15-len(key))} \t{variants[key].count(1) + variants[key].count(2) + variants[key].count(3) + variants[key].count(4)} '
            f"\t\t{variants[key].count(2) + variants[key].count(3) + variants[key].count(4)} "
            f"\t\t{variants[key].count(3) + variants[key].count(4)} "
            f"\t\t{variants[key].count(4)}"
        )
