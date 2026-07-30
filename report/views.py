
import pandas as pd
from django.shortcuts import render,redirect
from .forms import DatasetUploadForm
from .validators import validate_dataset
from .models import Doctor, Patient, Admission, Surgery
from .kpi_queries import get_full_scorecard, run_query

def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                doctors_df = pd.read_csv(request.FILES['doctors_csv'])
                patients_df = pd.read_csv(request.FILES['patients_csv'])
                admissions_df = pd.read_csv(request.FILES['admissions_csv'])
                surgeries_df = pd.read_csv(request.FILES['surgeries_csv'])
            except Exception as e:
                return render(request, 'report/upload.html', {
                    'form': form,
                    'errors': [f"Could not read one of the CSV files: {e}"],
                })

            result = validate_dataset(doctors_df, patients_df, admissions_df, surgeries_df)

            if not result['valid']:
                return render(request, 'report/upload.html', {
                    'form': form,
                    'errors': result['errors'],
                    'warnings': result['warnings'],
                })

            # Clear old data so re-uploads don't duplicate (simple approach for now)
            Surgery.objects.all().delete()
            Admission.objects.all().delete()
            Patient.objects.all().delete()
            Doctor.objects.all().delete()

            # Bulk insert Doctors
            doctors_objs = [
                Doctor(
                    doctor_id=row['doctor_id'],
                    name=row['name'],
                    department=row['department'],
                    specialization=row['specialization'],
                    years_experience=row['years_experience'],
                )
                for _, row in doctors_df.iterrows()
            ]
            Doctor.objects.bulk_create(doctors_objs)

            # Bulk insert Patients
            patients_objs = [
                Patient(
                    patient_id=row['patient_id'],
                    name=row['name'],
                    age=row['age'],
                    gender=row['gender'],
                )
                for _, row in patients_df.iterrows()
            ]
            Patient.objects.bulk_create(patients_objs)

            # Bulk insert Admissions
            admissions_objs = [
                Admission(
                    admission_id=row['admission_id'],
                    patient_id=row['patient_id'],
                    doctor_id=row['doctor_id'],
                    department=row['department'],
                    admission_date=row['admission_date'],
                    discharge_date=row['discharge_date'] if pd.notna(row['discharge_date']) else None,
                    condition_severity=row['condition_severity'],
                    admission_type=row['admission_type'],
                    outcome=row['outcome'],
                )
                for _, row in admissions_df.iterrows()
            ]
            Admission.objects.bulk_create(admissions_objs)

            # Bulk insert Surgeries
            surgeries_objs = [
                Surgery(
                    surgery_id=row['surgery_id'],
                    admission_id=row['admission_id'],
                    patient_id=row['patient_id'],
                    doctor_id=row['doctor_id'],
                    surgery_date=row['surgery_date'],
                    surgery_type=row['surgery_type'],
                    outcome=row['outcome'],
                )
                for _, row in surgeries_df.iterrows()
            ]
            Surgery.objects.bulk_create(surgeries_objs)

            return redirect('scorecard')
    else:
        form = DatasetUploadForm()

    return render(request, 'report/upload.html', {'form': form})


def scorecard(request):
    data = get_full_scorecard()

    # prep data for charts - Chart.js wants plain lists, not dicts
    dept_labels = [row['department'] for row in data['department_performance']]
    dept_admissions = [row['total_admissions'] for row in data['department_performance']]

    admission_outcomes = run_query("""
        SELECT outcome, COUNT(*) as count
        FROM report_admission
        WHERE outcome IS NOT NULL
        GROUP BY outcome
    """)
    surgery_outcomes = run_query("""
        SELECT outcome, COUNT(*) as count
        FROM report_surgery
        WHERE outcome IS NOT NULL
        GROUP BY outcome
    """)

    context = {
        'data': data,
        'dept_labels': dept_labels,
        'dept_admissions': dept_admissions,
        'admission_outcome_labels': [row['outcome'] for row in admission_outcomes],
        'admission_outcome_values': [row['count'] for row in admission_outcomes],
        'surgery_outcome_labels': [row['outcome'] for row in surgery_outcomes],
        'surgery_outcome_values': [row['count'] for row in surgery_outcomes],
    }
    return render(request, 'report/scorecard.html', context)


def custom_404(request, exception):
    return render(request, "report/404.html", status=404)


def custom_500(request):
    return render(request, "report/500.html", status=500)