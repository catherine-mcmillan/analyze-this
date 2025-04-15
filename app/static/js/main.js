// Common JavaScript functions and event handlers

// Show/hide loading spinner
function showLoading(buttonElement, loadingText = 'Processing...') {
    const originalText = buttonElement.innerHTML;
    buttonElement.disabled = true;
    buttonElement.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${loadingText}`;
    return originalText;
}

function hideLoading(buttonElement, originalText) {
    buttonElement.disabled = false;
    buttonElement.innerHTML = originalText;
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add loading indicators to form submits
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                showLoading(submitButton);
            }
        });
    });
});