from django import forms


class DatasetUploadForm(forms.Form):
    doctors_csv = forms.FileField(label="Doctors.csv")
    patients_csv = forms.FileField(label="Patients.csv")
    admissions_csv = forms.FileField(label="Admissions.csv")
    surgeries_csv = forms.FileField(label="Surgeries.csv")