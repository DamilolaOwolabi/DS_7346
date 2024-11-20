function toggleDropdown(button) {
    const dropdownMenu = button.nextElementSibling;
    const isVisible = dropdownMenu.style.display === "block";
    
    // Close any open dropdowns
    document.querySelectorAll('.dropdown-menu').forEach(menu => menu.style.display = 'none');
    
    // Toggle the clicked dropdown
    dropdownMenu.style.display = isVisible ? "none" : "block";
    
    // Update the aria-expanded attribute for accessibility
    button.setAttribute('aria-expanded', !isVisible);
}

// Close the dropdown if clicked outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.filter-label')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => menu.style.display = 'none');
    }
});
