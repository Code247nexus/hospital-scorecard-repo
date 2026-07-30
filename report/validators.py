import pandas as pd


REQUIRED_COLUMNS = {
    'doctors': ['doctor_id', 'name', 'department', 'specialization', 'years_experience'],
    'patients': ['patient_id', 'name', 'age', 'gender'],
    'admissions': ['admission_id', 'patient_id', 'doctor_id', 'department',
                   'admission_date', 'discharge_date', 'condition_severity',
                   'admission_type', 'outcome'],
    'surgeries': ['surgery_id', 'admission_id', 'patient_id', 'doctor_id',
                  'surgery_date', 'surgery_type', 'outcome'],
}

VALID_OUTCOMES_ADMISSIONS = {'Cured', 'Transferred', 'Deceased'}
VALID_OUTCOMES_SURGERIES = {'Success', 'Complication', 'Death'}
VALID_SEVERITY = {'Mild', 'Moderate', 'Critical'}


def validate_dataset(doctors_df, patients_df, admissions_df, surgeries_df):
    """
    Runs EDA-style validation checks on the four uploaded datasets.
    Returns a dict: {'valid': bool, 'errors': [...], 'warnings': [...], 'summary': {...}}
    """
    errors = []
    warnings = []

    dataframes = {
        'doctors': doctors_df,
        'patients': patients_df,
        'admissions': admissions_df,
        'surgeries': surgeries_df,
    }

    # 1. Required columns check
    for name, df in dataframes.items():
        missing_cols = set(REQUIRED_COLUMNS[name]) - set(df.columns)
        if missing_cols:
            errors.append(f"{name}.csv is missing required columns: {sorted(missing_cols)}")

    if errors:
        # Can't safely run further checks if columns are missing
        return {'valid': False, 'errors': errors, 'warnings': warnings, 'summary': {}}

    # 2. Missing values in critical fields
    for name, df in dataframes.items():
        null_counts = df[REQUIRED_COLUMNS[name]].isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                warnings.append(f"{name}.csv: {count} missing value(s) in '{col}'")

    # 3. Duplicate primary keys
    pk_map = {
        'doctors': 'doctor_id',
        'patients': 'patient_id',
        'admissions': 'admission_id',
        'surgeries': 'surgery_id',
    }
    for name, pk in pk_map.items():
        dup_count = dataframes[name][pk].duplicated().sum()
        if dup_count > 0:
            errors.append(f"{name}.csv has {dup_count} duplicate {pk} value(s)")

    # 4. Foreign key integrity
    invalid_patient_fk = ~admissions_df['patient_id'].isin(patients_df['patient_id'])
    if invalid_patient_fk.sum() > 0:
        errors.append(f"admissions.csv: {invalid_patient_fk.sum()} row(s) reference a patient_id not in patients.csv")

    invalid_doctor_fk = ~admissions_df['doctor_id'].isin(doctors_df['doctor_id'])
    if invalid_doctor_fk.sum() > 0:
        errors.append(f"admissions.csv: {invalid_doctor_fk.sum()} row(s) reference a doctor_id not in doctors.csv")

    invalid_surg_patient_fk = ~surgeries_df['patient_id'].isin(patients_df['patient_id'])
    if invalid_surg_patient_fk.sum() > 0:
        errors.append(f"surgeries.csv: {invalid_surg_patient_fk.sum()} row(s) reference a patient_id not in patients.csv")

    invalid_surg_doctor_fk = ~surgeries_df['doctor_id'].isin(doctors_df['doctor_id'])
    if invalid_surg_doctor_fk.sum() > 0:
        errors.append(f"surgeries.csv: {invalid_surg_doctor_fk.sum()} row(s) reference a doctor_id not in doctors.csv")

    invalid_surg_admission_fk = ~surgeries_df['admission_id'].isin(admissions_df['admission_id'])
    if invalid_surg_admission_fk.sum() > 0:
        errors.append(f"surgeries.csv: {invalid_surg_admission_fk.sum()} row(s) reference an admission_id not in admissions.csv")

    # 5. Categorical value sanity
    bad_outcomes_adm = set(admissions_df['outcome'].dropna().unique()) - VALID_OUTCOMES_ADMISSIONS
    if bad_outcomes_adm:
        warnings.append(f"admissions.csv has unexpected outcome values: {bad_outcomes_adm}")

    bad_outcomes_surg = set(surgeries_df['outcome'].dropna().unique()) - VALID_OUTCOMES_SURGERIES
    if bad_outcomes_surg:
        warnings.append(f"surgeries.csv has unexpected outcome values: {bad_outcomes_surg}")

    bad_severity = set(admissions_df['condition_severity'].dropna().unique()) - VALID_SEVERITY
    if bad_severity:
        warnings.append(f"admissions.csv has unexpected condition_severity values: {bad_severity}")

    # 6. Outcome-rate sanity (flag if wildly implausible, not a hard error)
    if len(admissions_df) > 0:
        cure_rate = (admissions_df['outcome'] == 'Cured').sum() / admissions_df['outcome'].count() * 100
        if cure_rate < 50 or cure_rate > 99:
            warnings.append(f"Recovery rate looks unusual: {cure_rate:.1f}% (expected roughly 70-95%)")

    if len(surgeries_df) > 0:
        mortality_rate = (surgeries_df['outcome'] == 'Death').sum() / surgeries_df['outcome'].count() * 100
        if mortality_rate > 15:
            warnings.append(f"Surgical mortality rate looks unusually high: {mortality_rate:.1f}%")

    # Summary for display
    summary = {
        'doctors_count': len(doctors_df),
        'patients_count': len(patients_df),
        'admissions_count': len(admissions_df),
        'surgeries_count': len(surgeries_df),
    }

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'summary': summary,
    }