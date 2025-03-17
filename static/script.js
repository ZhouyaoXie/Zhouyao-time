document.addEventListener("DOMContentLoaded", function() {
  const colors = ['#F17300', '#6096BA'];

  function colorizeRandomWords(text) {
    const words = text.split(' ');
    const indices = new Set();
    
    // Select 3 random unique indices
    while(indices.size < 3 && indices.size < words.length) {
      indices.add(Math.floor(Math.random() * words.length));
    }
    
    // Wrap selected words with colored spans
    return words.map((word, index) => {
      if(indices.has(index)) {
        const color = colors[Array.from(indices).indexOf(index)];
        return `<span style="color: ${color}">${word}</span>`;
      }
      return word;
    }).join(' ');
  }

  const logger = {
    error: function(message, error) {
      console.error(message, error);
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
        header.className = 'cyberpunk-entry';
        header.innerHTML = colorizeRandomWords(entry);
        entriesContainer.appendChild(header);

        // After animation completes, remove the cyberpunk effects
        setTimeout(() => {
          header.style.animation = 'none';
          header.style.opacity = '1';
          header.style.transform = 'none';
        }, 2500);
      });
    })
    .catch(error => {
      logger.error("Error fetching entries:", error);
      document.getElementById('entries').innerHTML = "<p>Error loading entry.</p>";
    });
});