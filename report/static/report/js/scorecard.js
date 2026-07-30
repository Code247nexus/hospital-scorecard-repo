document.addEventListener('DOMContentLoaded', function () {
    // department admissions - bar chart
    const deptLabels = JSON.parse(document.getElementById('dept-labels').textContent);
    const deptData = JSON.parse(document.getElementById('dept-data').textContent);

    new Chart(document.getElementById('deptChart'), {
        type: 'bar',
        data: {
            labels: deptLabels,
            datasets: [{ label: 'Admissions', data: deptData, backgroundColor: '#0d9488' }]
        },
        options: { responsive: true }
    });

    // admission outcome - donut
    const admissionLabels = JSON.parse(document.getElementById('admission-outcome-labels').textContent);
    const admissionValues = JSON.parse(document.getElementById('admission-outcome-values').textContent);

    new Chart(document.getElementById('admissionOutcomeChart'), {
        type: 'doughnut',
        data: {
            labels: admissionLabels,
            datasets: [{ data: admissionValues, backgroundColor: ['#0d9488', '#f59e0b', '#dc2626'] }]
        },
        options: { responsive: true }
    });

    // surgery outcome - donut
    const surgeryLabels = JSON.parse(document.getElementById('surgery-outcome-labels').textContent);
    const surgeryValues = JSON.parse(document.getElementById('surgery-outcome-values').textContent);

    new Chart(document.getElementById('surgeryOutcomeChart'), {
        type: 'doughnut',
        data: {
            labels: surgeryLabels,
            datasets: [{ data: surgeryValues, backgroundColor: ['#0d9488', '#f59e0b', '#dc2626'] }]
        },
        options: { responsive: true }
    });
});s