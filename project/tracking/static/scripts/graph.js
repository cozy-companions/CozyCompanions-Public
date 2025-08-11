// Dynamic chart logic for progress chart page
document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('dynamicChart');
    
    // Check if the canvas element exists on the page
    if (canvas) {
        // Read both the URL and the slug from the data attributes
        const dataUrl = canvas.dataset.url;
        const slug = canvas.dataset.slug; // <-- Read the slug

        // Set chart type and options based on slug
        let chartType = 'line';
        let chartOptions = { // Default options for line charts
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };

        // Use bar chart for social-development
        if (slug === 'social-development') {
            chartType = 'bar';
            chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1 
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            };
        }

        // Fetch chart data and render
        fetch(dataUrl)
            .then(response => response.json())
            .then(data => {
                const chartLabel = data.question_text || 'Score'; 

                new Chart(canvas, {
                    type: chartType,
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: chartLabel,
                            data: data.values,
                            fill: true,
                            borderColor: '#e7388a',
                            backgroundColor: 'rgba(231, 56, 138, 0.18)',
                            tension: 0.1
                        }]
                    },
                    options: chartOptions
                });
            })
            .catch(error => {
                console.error('Error fetching chart data:', error);
            });
    }
});