from django.db import models

# Create your models here.



class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    years_experience = models.IntegerField()

    def __str__(self):
        return self.name


class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Admission(models.Model):
    OUTCOME_CHOICES = [
        ('Cured', 'Cured'),
        ('Transferred', 'Transferred'),
        ('Deceased', 'Deceased'),
    ]
    SEVERITY_CHOICES = [
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Critical', 'Critical'),
    ]
    TYPE_CHOICES = [
        ('Planned', 'Planned'),
        ('Emergency', 'Emergency'),
    ]

    admission_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)
    admission_date = models.DateField()
    discharge_date = models.DateField(null=True, blank=True)
    condition_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    admission_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)

    def __str__(self):
        return f"Admission {self.admission_id} - Patient {self.patient_id}"


class Surgery(models.Model):
    OUTCOME_CHOICES = [
        ('Success', 'Success'),
        ('Complication', 'Complication'),
        ('Death', 'Death'),
    ]

    surgery_id = models.AutoField(primary_key=True)
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    surgery_date = models.DateField()
    surgery_type = models.CharField(max_length=100)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)

    def __str__(self):
        return f"Surgery {self.surgery_id} - {self.surgery_type}"