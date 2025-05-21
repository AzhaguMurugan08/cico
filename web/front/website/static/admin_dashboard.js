// Toggle User Dropdown
function toggleUserDropdown() {
  const dropdown = document.getElementById('userInfo');
  // Toggle dropdown visibility
  dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

// Toggle Section visibility based on clicked section
function toggleSection(id) {
  document.querySelectorAll('.table-section').forEach(section => {
    section.style.display = 'none';
  });
  const target = document.getElementById(id);
  if (target) {
    target.style.display = 'block';
  }
}

// Close dropdown when clicking outside of it
document.addEventListener('click', function(event) {
  const dropdown = document.getElementById('userInfo');
  const trigger = document.querySelector('.user-info');

  if (dropdown && trigger && !trigger.contains(event.target)) {
    dropdown.style.display = 'none';
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const downloadButton = document.getElementById("download-checkin");

  downloadButton.addEventListener("click", function () {
    const rows = [];
    const tables = document.querySelectorAll("#checkin-section table tbody");

    // Loop through all tables in the Check-In section
    tables.forEach((tbody) => {
      const date = tbody.closest(".table-wrapper").previousElementSibling.textContent.trim();
      const rowsForDate = Array.from(tbody.querySelectorAll("tr")).map((row) => {
        const cells = Array.from(row.querySelectorAll("td")).map((cell) => cell.textContent.trim());
        return [date, ...cells]; // Add the date as the first column
      });
      rows.push(...rowsForDate);
    });

    // Generate CSV content
    const csvContent = [
      ["Date", "Name", "Roll No", "Department", "Year", "Time"], // Header row
      ...rows,
    ]
      .map((row) => row.join(","))
      .join("\n");

    // Create a Blob and trigger download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "checkin_records.csv";
    a.click();
    URL.revokeObjectURL(url);
  });
});
