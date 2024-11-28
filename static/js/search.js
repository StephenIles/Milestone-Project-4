document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.search-form');
    const filters = form.querySelectorAll('select, input[type="checkbox"]');
    
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            form.submit();
        });
    });
});
