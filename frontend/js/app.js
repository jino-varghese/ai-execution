// Configuration - Update this after deploying to AWS
const CONFIG = {
    // This will be replaced with actual API Gateway URL after Terraform deployment
    API_ENDPOINT: 'API_GATEWAY_URL_HERE'
};

// DOM Elements
const form = document.getElementById('itineraryForm');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const itineraryContent = document.getElementById('itineraryContent');
const generateBtn = document.getElementById('generateBtn');
const newItineraryBtn = document.getElementById('newItineraryBtn');

// Event Listeners
form.addEventListener('submit', handleFormSubmit);
newItineraryBtn.addEventListener('click', resetForm);

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault();

    // Collect form data
    const formData = {
        destination: document.getElementById('destination').value,
        duration: parseInt(document.getElementById('duration').value),
        budget: document.getElementById('budget').value,
        interests: Array.from(document.querySelectorAll('input[name="interests"]:checked'))
            .map(cb => cb.value),
        travelStyle: document.getElementById('travelStyle').value,
        preferences: document.getElementById('preferences').value
    };

    // Validate
    if (formData.interests.length === 0) {
        alert('Please select at least one interest');
        return;
    }

    // Show loading state
    form.classList.add('hidden');
    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');

    try {
        // Call API
        const itinerary = await generateItinerary(formData);

        // Display results
        displayItinerary(itinerary);

        loadingDiv.classList.add('hidden');
        resultsDiv.classList.remove('hidden');
    } catch (error) {
        console.error('Error generating itinerary:', error);
        alert('Failed to generate itinerary. Please try again.');
        loadingDiv.classList.add('hidden');
        form.classList.remove('hidden');
    }
}

// API call to generate itinerary
async function generateItinerary(formData) {
    // Check if API endpoint is configured
    if (CONFIG.API_ENDPOINT === 'API_GATEWAY_URL_HERE') {
        // For local testing - return mock data
        return generateMockItinerary(formData);
    }

    // Production API call
    const response = await fetch(CONFIG.API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    });

    if (!response.ok) {
        throw new Error('API request failed');
    }

    const data = await response.json();
    return data.itinerary || data;
}

// Mock itinerary generator for local testing
function generateMockItinerary(formData) {
    return new Promise((resolve) => {
        setTimeout(() => {
            const itinerary = {
                destination: formData.destination,
                duration: formData.duration,
                budget: formData.budget,
                summary: `A ${formData.duration}-day ${formData.budget} trip to ${formData.destination} tailored for ${formData.travelStyle} travelers interested in ${formData.interests.join(', ')}.`,
                days: []
            };

            // Generate daily itinerary
            for (let i = 1; i <= formData.duration; i++) {
                const activities = generateDayActivities(i, formData);
                itinerary.days.push({
                    day: i,
                    activities: activities
                });
            }

            resolve(itinerary);
        }, 2000);
    });
}

// Generate activities for a specific day
function generateDayActivities(day, formData) {
    const activities = [];
    const { interests, budget, destination } = formData;

    if (day === 1) {
        activities.push({
            time: 'Morning',
            activity: `Arrive in ${destination} and check into hotel`,
            description: 'Settle in and freshen up'
        });
        activities.push({
            time: 'Afternoon',
            activity: 'Orientation walk and local exploration',
            description: 'Get familiar with the neighborhood, visit nearby attractions'
        });
    } else if (day === formData.duration) {
        activities.push({
            time: 'Morning',
            activity: 'Last-minute shopping and souvenir hunting',
            description: 'Pick up memorable items and gifts'
        });
        activities.push({
            time: 'Afternoon',
            activity: `Departure from ${destination}`,
            description: 'Check out and head to airport'
        });
    } else {
        // Generate based on interests
        if (interests.includes('culture')) {
            activities.push({
                time: 'Morning',
                activity: 'Visit museums and historical sites',
                description: `Explore ${destination}'s rich cultural heritage`
            });
        }
        if (interests.includes('food')) {
            activities.push({
                time: 'Lunch',
                activity: 'Local food tour or cooking class',
                description: 'Experience authentic local cuisine'
            });
        }
        if (interests.includes('adventure')) {
            activities.push({
                time: 'Afternoon',
                activity: 'Adventure activities or outdoor sports',
                description: 'Hiking, cycling, or water sports'
            });
        }
        if (interests.includes('nature')) {
            activities.push({
                time: 'Morning',
                activity: 'Nature reserve or park visit',
                description: 'Enjoy the natural beauty and wildlife'
            });
        }
        if (interests.includes('shopping')) {
            activities.push({
                time: 'Afternoon',
                activity: 'Shopping district exploration',
                description: 'Browse local markets and boutiques'
            });
        }
        if (interests.includes('relaxation')) {
            activities.push({
                time: 'Evening',
                activity: 'Spa or wellness experience',
                description: 'Unwind and rejuvenate'
            });
        }

        // Ensure at least 3 activities per day
        while (activities.length < 3) {
            activities.push({
                time: 'Evening',
                activity: `Dinner at ${budget === 'luxury' ? 'fine dining restaurant' : budget === 'budget' ? 'local eatery' : 'popular restaurant'}`,
                description: 'Enjoy local specialties'
            });
        }
    }

    return activities;
}

// Display itinerary in the UI
function displayItinerary(itinerary) {
    let html = '';

    // Summary section
    html += `
        <div class="summary-section">
            <h3>Trip Summary</h3>
            <p><strong>Destination:</strong> ${itinerary.destination}</p>
            <p><strong>Duration:</strong> ${itinerary.duration} days</p>
            <p><strong>Budget:</strong> ${itinerary.budget}</p>
            <p><strong>Overview:</strong> ${itinerary.summary}</p>
        </div>
    `;

    // Daily itinerary
    itinerary.days.forEach(day => {
        html += `
            <div class="day-section">
                <h3>Day ${day.day}</h3>
        `;

        day.activities.forEach(activity => {
            html += `
                <div class="activity">
                    <strong>${activity.time}:</strong> ${activity.activity}
                    ${activity.description ? `<br><em>${activity.description}</em>` : ''}
                </div>
            `;
        });

        html += '</div>';
    });

    itineraryContent.innerHTML = html;
}

// Reset form
function resetForm() {
    form.reset();
    form.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
}

// Initialize
console.log('AI Travel Itinerary Generator initialized');
if (CONFIG.API_ENDPOINT === 'API_GATEWAY_URL_HERE') {
    console.log('Running in demo mode - using mock data');
}
