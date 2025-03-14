document.addEventListener("DOMContentLoaded", function() {
  const logger = {
    error: function(message, error) {
      console.error(message, error);
      // Could add additional logging functionality here like sending to a logging service
    }
  };

  fetch('/api/current-entry')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
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
      logger.error("Error fetching entries:", error);
      document.getElementById('entries').innerHTML = "<p>Error loading entry.</p>";
    });
});
