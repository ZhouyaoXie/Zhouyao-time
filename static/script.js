document.addEventListener("DOMContentLoaded", function() {
  fetch('/api/current-entry')
    .then(response => response.json())
    .then(data => {
      const entriesContainer = document.getElementById('entries');
      // Clear the loading message
      entriesContainer.innerHTML = "";
      // Assuming data.entries is an array of strings
      data.entries.forEach(entry => {
        const header = document.createElement('h1');
        header.textContent = entry;
        entriesContainer.appendChild(header);
      });
    })
    .catch(error => {
      console.error("Error fetching entries:", error);
      document.getElementById('entries').innerHTML = "<p>Error loading entry.</p>";
    });
});
