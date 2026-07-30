document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('upload-form');
    const btn = document.getElementById('analyze-btn');
    const loadingMsg = document.getElementById('loading-msg');

    if (form) {
        form.addEventListener('submit', function () {
            btn.disabled = true;
            btn.innerText = "Analyzing...";
            loadingMsg.style.display = "block";
        });
    }
});