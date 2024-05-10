function sendQuery() {
    const userInput = document.getElementById('userInput').value;
    const responseArea = document.getElementById('responseArea');

    fetch('http://127.0.0.1:5000/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userInput })
    })
    .then(response => response.json())
    .then(data => {
        responseArea.innerHTML = ''; // Clear previous content
        if (Array.isArray(data.recommendations) && data.recommendations.length > 0) {
            data.recommendations.forEach(restaurant => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div class="card-header">${restaurant.name}</div>
                    <div class="card-body">${restaurant.description}</div>
                `;
                responseArea.appendChild(card);
            });
        } else {
            responseArea.innerHTML = 'No recommendations found or error in response.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        responseArea.innerHTML = 'Failed to fetch recommendations.';
    });
}
