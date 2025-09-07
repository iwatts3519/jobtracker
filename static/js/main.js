// Main JavaScript functionality for Job Tracker

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle delete job buttons
    $('.delete-job').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var jobId = $(this).data('job-id');
        var jobTitle = $(this).closest('.job-card').find('.card-title').text();
        
        if (confirm('Are you sure you want to delete "' + jobTitle + '"?')) {
            // Create a form and submit it
            var form = $('<form method="POST" action="/delete_job/' + jobId + '">');
            $('body').append(form);
            form.submit();
        }
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add loading states to buttons
    $('form').submit(function() {
        var submitBtn = $(this).find('button[type="submit"]');
        var originalText = submitBtn.html();
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2" role="status"></span>Saving...');
        submitBtn.prop('disabled', true);
    });

    // Validate job URL format
    $('#url').on('blur', function() {
        var url = $(this).val();
        // More flexible URL pattern that handles query parameters, fragments, and special characters
        var urlPattern = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;
        
        if (url && !urlPattern.test(url)) {
            $(this).addClass('is-invalid');
            if (!$(this).next('.invalid-feedback').length) {
                $(this).after('<div class="invalid-feedback">Please enter a valid URL starting with http:// or https://</div>');
            }
        } else {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
        }
    });

    // Character counter for description field
    $('#description').on('input', function() {
        var maxLength = 5000;
        var currentLength = $(this).val().length;
        var remaining = maxLength - currentLength;
        
        if (!$('#char-counter').length) {
            $(this).after('<div id="char-counter" class="form-text"></div>');
        }
        
        $('#char-counter').text(remaining + ' characters remaining');
        
        if (remaining < 0) {
            $(this).addClass('is-invalid');
            $('#char-counter').addClass('text-danger');
        } else {
            $(this).removeClass('is-invalid');
            $('#char-counter').removeClass('text-danger');
        }
    });
});