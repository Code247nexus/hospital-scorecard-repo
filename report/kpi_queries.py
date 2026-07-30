from django.db import connection


def run_query(sql):
    # small helper so I don't repeat cursor code everywhere
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def get_doctor_count():
    total = run_query("SELECT COUNT(*) as total FROM report_doctor")[0]['total']

    by_dept = run_query("""
        SELECT department, COUNT(*) as count
        FROM report_doctor
        GROUP BY department
        ORDER BY count DESC
    """)

    return {'total': total, 'by_department': by_dept}


def get_recovery_rate():
    result = run_query("""
        SELECT
            SUM(CASE WHEN outcome = 'Cured' THEN 1 ELSE 0 END) as cured,
            COUNT(*) as total
        FROM report_admission
        WHERE outcome IS NOT NULL
    """)[0]

    if result['total'] == 0:
        return 0

    return round(result['cured'] / result['total'] * 100, 2)


def get_surgical_mortality_rate():
    result = run_query("""
        SELECT
            SUM(CASE WHEN outcome = 'Death' THEN 1 ELSE 0 END) as deaths,
            COUNT(*) as total
        FROM report_surgery
        WHERE outcome IS NOT NULL
    """)[0]

    if result['total'] == 0:
        return 0

    return round(result['deaths'] / result['total'] * 100, 2)


def get_critical_survival_rate():
    result = run_query("""
        SELECT
            SUM(CASE WHEN outcome = 'Cured' THEN 1 ELSE 0 END) as cured,
            COUNT(*) as total
        FROM report_admission
        WHERE condition_severity = 'Critical' AND outcome IS NOT NULL
    """)[0]

    if result['total'] == 0:
        return 0

    return round(result['cured'] / result['total'] * 100, 2)


def get_department_performance():
    # avg length of stay only counts admissions that actually have a discharge date
    rows = run_query("""
        SELECT
            department,
            COUNT(*) as total_admissions,
            SUM(CASE WHEN outcome = 'Cured' THEN 1 ELSE 0 END) as cured,
            SUM(CASE WHEN outcome = 'Deceased' THEN 1 ELSE 0 END) as deceased,
            AVG(CASE WHEN discharge_date IS NOT NULL
                THEN DATEDIFF(discharge_date, admission_date) END) as avg_los
        FROM report_admission
        WHERE outcome IS NOT NULL
        GROUP BY department
        ORDER BY total_admissions DESC
    """)

    # calculate the percentages here instead of in SQL, easier to read
    for row in rows:
        row['recovery_rate_pct'] = round(row['cured'] / row['total_admissions'] * 100, 2)
        row['mortality_rate_pct'] = round(row['deceased'] / row['total_admissions'] * 100, 2)
        row['avg_length_of_stay_days'] = round(row['avg_los'], 1) if row['avg_los'] is not None else None

    return rows


def get_readmission_rate():
    total_patients = run_query("SELECT COUNT(*) as total FROM report_patient")[0]['total']

    if total_patients == 0:
        return 0

    result = run_query("""
        SELECT COUNT(*) as readmitted_count FROM (
            SELECT patient_id
            FROM report_admission
            GROUP BY patient_id
            HAVING COUNT(*) > 1
        ) as sub
    """)[0]

    return round(result['readmitted_count'] / total_patients * 100, 2)


def get_doctor_workload():
    # how many admissions each doctor has handled - shows who's overloaded
    rows = run_query("""
        SELECT
            d.doctor_id,
            d.name,
            d.department,
            COUNT(a.admission_id) as admissions_handled
        FROM report_doctor d
        LEFT JOIN report_admission a ON a.doctor_id = d.doctor_id
        GROUP BY d.doctor_id, d.name, d.department
        ORDER BY admissions_handled DESC
    """)
    return rows


def get_avg_length_of_stay():
    # hospital-wide average length of stay, not split by department
    result = run_query("""
        SELECT AVG(DATEDIFF(discharge_date, admission_date)) as avg_los
        FROM report_admission
        WHERE discharge_date IS NOT NULL
    """)[0]

    if result['avg_los'] is None:
        return 0

    return round(result['avg_los'], 1)


def get_full_scorecard():
    # pulls everything together for the results page
    return {
        'doctor_count': get_doctor_count(),
        'recovery_rate': get_recovery_rate(),
        'surgical_mortality_rate': get_surgical_mortality_rate(),
        'critical_survival_rate': get_critical_survival_rate(),
        'department_performance': get_department_performance(),
        'readmission_rate': get_readmission_rate(),
        'doctor_workload': get_doctor_workload(),
        'avg_length_of_stay': get_avg_length_of_stay(),
    }