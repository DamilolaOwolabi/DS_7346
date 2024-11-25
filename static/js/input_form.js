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

function updateSelectedBrand(select) {
    const button = select.previousElementSibling;
    const selectedOption = select.options[select.selectedIndex].text;
    button.textContent = `Brand: ${selectedOption}`;
    select.style.display = 'none'; // Hide dropdown after selection
    button.setAttribute('aria-expanded', 'false');
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("filter-form");
    const submitButton = document.getElementById("submit-button");

    if (form && submitButton) {
        // Prevent results sorter from being triggered on button clicks except submit
        form.addEventListener("submit", function (e) {
            const submitAction = e.submitter; // Determine the clicked button
            if (submitAction && submitAction.id !== "submit-button") {
                e.preventDefault(); // Stop non-submit buttons from re-sorting
            }
        });
    }
});


// Close the dropdown if clicked outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.filter-label')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => menu.style.display = 'none');
    }
});


