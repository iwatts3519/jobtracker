// Kanban board drag and drop functionality

$(document).ready(function() {
    // Initialize sortable for all kanban columns
    $('.kanban-content').sortable({
        connectWith: '.kanban-content',
        items: '.job-card',
        cursor: 'move',
        opacity: 0.8,
        placeholder: 'sortable-placeholder',
        tolerance: 'pointer',
        helper: function(e, ui) {
            // Make the helper card slightly smaller and rotated
            ui.addClass('ui-sortable-helper');
            return ui;
        },
        start: function(e, ui) {
            // Add some visual feedback when dragging starts
            ui.item.addClass('dragging');
            ui.placeholder.height(ui.item.outerHeight());
        },
        stop: function(e, ui) {
            // Remove visual feedback when dragging stops
            ui.item.removeClass('dragging ui-sortable-helper');
        },
        update: function(e, ui) {
            // Only trigger update if item was moved to a different column
            var newColumn = ui.item.closest('.kanban-column');
            var newStatus = newColumn.data('status');
            var jobId = ui.item.data('job-id');
            
            // Update job status via AJAX
            updateJobStatus(jobId, newStatus);
            
            // Update column counts
            updateColumnCounts();
        },
        receive: function(e, ui) {
            // This fires when an item is moved from another column
            var newColumn = ui.item.closest('.kanban-column');
            var newStatus = newColumn.data('status');
            var jobId = ui.item.data('job-id');
            
            // Update job status via AJAX
            updateJobStatus(jobId, newStatus);
            
            // Update column counts
            updateColumnCounts();
        }
    }).disableSelection();

    // Add touch support for mobile devices
    if ('ontouchstart' in window) {
        $('.kanban-content').sortable('option', 'cancel', 'input,textarea,button,select,option,.btn');
    }
});

function updateJobStatus(jobId, newStatus) {
    // Show loading indicator
    var jobCard = $('[data-job-id="' + jobId + '"]');
    jobCard.addClass('loading');
    
    $.ajax({
        url: '/update_job_status',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            'job_id': jobId,
            'status': newStatus
        }),
        success: function(response) {
            if (response.success) {
                // Remove loading indicator
                jobCard.removeClass('loading');
                
                // Show success feedback
                showToast('Job status updated successfully!', 'success');
                
                // Update the applied date if moved to applied status
                if (newStatus === 'applied') {
                    var now = new Date();
                    var dateStr = (now.getMonth() + 1) + '/' + now.getDate() + '/' + now.getFullYear();
                    jobCard.find('.text-muted:contains("Applied:")').text('Applied: ' + dateStr);
                }
            } else {
                // Handle error
                handleStatusUpdateError(jobCard, 'Server error occurred');
            }
        },
        error: function(xhr, status, error) {
            handleStatusUpdateError(jobCard, 'Failed to update job status');
        }
    });
}

function handleStatusUpdateError(jobCard, message) {
    jobCard.removeClass('loading');
    showToast(message + '. Please try again.', 'error');
    
    // Revert the card position (reload page as simple solution)
    setTimeout(function() {
        location.reload();
    }, 2000);
}

function updateColumnCounts() {
    $('.kanban-column').each(function() {
        var column = $(this);
        var count = column.find('.job-card').length;
        var header = column.find('.kanban-header h5');
        var text = header.text();
        var newText = text.replace(/\(\d+\)/, '(' + count + ')');
        header.text(newText);
    });
}

function showToast(message, type) {
    // Create toast notification
    var toastClass = type === 'success' ? 'bg-success' : 'bg-danger';
    var toast = $(`
        <div class="toast align-items-center text-white ${toastClass} border-0" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    
    // Show toast
    var bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    // Remove from DOM after it's hidden
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Add keyboard shortcuts
$(document).keydown(function(e) {
    // Ctrl+N to add new job
    if (e.ctrlKey && e.keyCode === 78) {
        e.preventDefault();
        window.location.href = '/add_job';
    }
    
    // ESC to close any open dropdowns
    if (e.keyCode === 27) {
        $('.dropdown-menu').removeClass('show');
    }
});