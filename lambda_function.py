import json
import boto3
from datetime import datetime
import urllib3
import os

# Initialize HTTP client for API calls
http = urllib3.PoolManager()

# Define available cities with their coordinates
CITIES = {
    'houston': {'name': 'Houston, Texas', 'lat': 29.7604, 'lon': -95.3698},
    'newyork': {'name': 'New York, NY', 'lat': 40.7128, 'lon': -74.0060},
    'losangeles': {'name': 'Los Angeles, CA', 'lat': 34.0522, 'lon': -118.2437},
    'chicago': {'name': 'Chicago, IL', 'lat': 41.8781, 'lon': -87.6298},
    'miami': {'name': 'Miami, FL', 'lat': 25.7617, 'lon': -80.1918},
    'seattle': {'name': 'Seattle, WA', 'lat': 47.6062, 'lon': -122.3321},
    'boston': {'name': 'Boston, MA', 'lat': 42.3601, 'lon': -71.0589},
    'sanfrancisco': {'name': 'San Francisco, CA', 'lat': 37.7749, 'lon': -122.4194},
    'austin': {'name': 'Austin, TX', 'lat': 30.2672, 'lon': -97.7431},
    'denver': {'name': 'Denver, CO', 'lat': 39.7392, 'lon': -104.9903}
}

def lambda_handler(event, context):
    """
    Main Lambda handler function that serves a web UI with weather info and service selection
    
    This function:
    1. Displays current time and weather for selected city
    2. Provides city dropdown for location selection
    3. Provides service selection options for Gen AI services
    4. Handles GET (display UI), POST (process selections), and weather API requests
    """
    
    # Get the HTTP method from the event
    http_method = event.get('httpMethod', 'GET')
    
    if http_method == 'GET':
        # Check if this is a weather API request
        query_params = event.get('queryStringParameters') or {}
        if 'city' in query_params:
            # Return weather data for the requested city
            city_key = query_params.get('city', 'houston')
            weather = get_weather_data(city_key)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(weather)
            }
        else:
            # Serve the main web UI
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                },
                'body': get_html_page()
            }
    
    elif http_method == 'POST':
        # Handle service selection
        try:
            body = json.loads(event.get('body', '{}'))
            selected_service = body.get('service', 'none')
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'message': f'Selected service: {selected_service}',
                    'service': selected_service,
                    'timestamp': datetime.now().isoformat()
                })
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

def get_weather_data(city_key='houston'):
    """
    Fetch weather data for specified city
    Uses OpenWeatherMap API (you'll need to add your API key)
    
    Args:
        city_key: Key from CITIES dictionary (default: 'houston')
    """
    try:
        # You'll need to set this as an environment variable in Lambda
        api_key = os.environ.get('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')
        
        # Get city coordinates
        city = CITIES.get(city_key, CITIES['houston'])
        lat = city['lat']
        lon = city['lon']
        
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=imperial'
        
        response = http.request('GET', url)
        weather_data = json.loads(response.data.decode('utf-8'))
        
        return {
            'city': city['name'],
            'temperature': weather_data['main']['temp'],
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity'],
            'feels_like': weather_data['main']['feels_like']
        }
    except Exception as e:
        # Return default data if API call fails
        return {
            'city': CITIES.get(city_key, CITIES['houston'])['name'],
            'temperature': 'N/A',
            'description': 'Unable to fetch weather',
            'humidity': 'N/A',
            'feels_like': 'N/A',
            'error': str(e)
        }

def get_html_page():
    """
    Generate the HTML page with embedded CSS and JavaScript
    """
    
    # Get current time and default weather (Houston)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    weather = get_weather_data('houston')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AWS Gen AI Dashboard - Multi-City Weather</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 900px;
                margin: 0 auto;
            }}
            
            .header {{
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            
            h1 {{
                color: #667eea;
                margin-bottom: 10px;
            }}
            
            .city-selector {{
                margin: 20px 0;
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .city-selector label {{
                font-weight: bold;
                color: #667eea;
                font-size: 16px;
            }}
            
            .city-selector select {{
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #667eea;
                border-radius: 10px;
                font-size: 16px;
                background: white;
                color: #333;
                cursor: pointer;
                transition: all 0.3s;
            }}
            
            .city-selector select:hover {{
                border-color: #764ba2;
                box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
            }}
            
            .city-selector select:focus {{
                outline: none;
                border-color: #764ba2;
                box-shadow: 0 0 15px rgba(102, 126, 234, 0.5);
            }}
            
            .loading {{
                display: none;
                color: #667eea;
                font-style: italic;
            }}
            
            .loading.active {{
                display: inline;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            
            .info-card {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                transition: transform 0.3s;
            }}
            
            .info-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .info-card h3 {{
                color: #667eea;
                font-size: 14px;
                margin-bottom: 5px;
            }}
            
            .info-card p {{
                color: #333;
                font-size: 18px;
                font-weight: bold;
            }}
            
            .services-section {{
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            
            .services-section h2 {{
                color: #667eea;
                margin-bottom: 20px;
            }}
            
            .service-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }}
            
            .service-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
                border: 2px solid transparent;
            }}
            
            .service-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            }}
            
            .service-card.selected {{
                border: 2px solid #ffd700;
                box-shadow: 0 0 20px rgba(255,215,0,0.5);
            }}
            
            .service-card h3 {{
                margin-bottom: 10px;
            }}
            
            .service-card p {{
                font-size: 14px;
                opacity: 0.9;
            }}
            
            .action-button {{
                background: #667eea;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 20px;
                transition: background 0.3s;
            }}
            
            .action-button:hover {{
                background: #764ba2;
            }}
            
            .response-area {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
            }}
            
            .response-area.active {{
                display: block;
            }}
            
            .weather-icon {{
                font-size: 40px;
                margin-bottom: 10px;
            }}
            
            .pulse {{
                animation: pulse 1s ease-in-out;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header Section with Time and Weather -->
            <div class="header">
                <h1>🚀 AWS Gen AI Dashboard</h1>
                
                <!-- City Selector Dropdown -->
                <div class="city-selector">
                    <label for="city-select">📍 Select City:</label>
                    <select id="city-select" onchange="changeCity()">
                        <option value="houston" selected>Houston, Texas</option>
                        <option value="newyork">New York, NY</option>
                        <option value="losangeles">Los Angeles, CA</option>
                        <option value="chicago">Chicago, IL</option>
                        <option value="miami">Miami, FL</option>
                        <option value="seattle">Seattle, WA</option>
                        <option value="boston">Boston, MA</option>
                        <option value="sanfrancisco">San Francisco, CA</option>
                        <option value="austin">Austin, TX</option>
                        <option value="denver">Denver, CO</option>
                    </select>
                    <span class="loading" id="loading">Loading...</span>
                </div>
                
                <p style="color: #666;" id="city-name">{weather['city']}</p>
                
                <div class="info-grid" id="weather-grid">
                    <div class="info-card">
                        <h3>🕐 Current Time</h3>
                        <p id="current-time">{current_time}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>🌡️ Temperature</h3>
                        <p id="temperature">{weather['temperature']}°F</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>☁️ Conditions</h3>
                        <p id="conditions">{weather['description'].title()}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>💧 Humidity</h3>
                        <p id="humidity">{weather['humidity']}%</p>
                    </div>
                </div>
            </div>
            
            <!-- Services Section -->
            <div class="services-section">
                <h2>Select an AWS Gen AI Service</h2>
                
                <div class="service-grid">
                    <div class="service-card" data-service="bedrock" onclick="selectService(this)">
                        <h3>🤖 Amazon Bedrock</h3>
                        <p>Build and scale Gen AI applications with foundation models</p>
                    </div>
                    
                    <div class="service-card" data-service="sagemaker" onclick="selectService(this)">
                        <h3>📊 SageMaker</h3>
                        <p>Train, deploy, and manage ML models at scale</p>
                    </div>
                    
                    <div class="service-card" data-service="comprehend" onclick="selectService(this)">
                        <h3>📝 Amazon Comprehend</h3>
                        <p>Natural language processing and text analytics</p>
                    </div>
                    
                    <div class="service-card" data-service="lex" onclick="selectService(this)">
                        <h3>💬 Amazon Lex</h3>
                        <p>Build conversational interfaces and chatbots</p>
                    </div>
                    
                    <div class="service-card" data-service="polly" onclick="selectService(this)">
                        <h3>🔊 Amazon Polly</h3>
                        <p>Turn text into lifelike speech</p>
                    </div>
                    
                    <div class="service-card" data-service="rekognition" onclick="selectService(this)">
                        <h3>👁️ Amazon Rekognition</h3>
                        <p>Image and video analysis</p>
                    </div>
                </div>
                
                <button class="action-button" onclick="submitService()">Launch Selected Service</button>
                
                <div class="response-area" id="response-area">
                    <h3>Service Information</h3>
                    <p id="response-text"></p>
                </div>
            </div>
        </div>
        
        <script>
            let selectedService = null;
            
            // Update time every second
            setInterval(() => {{
                const now = new Date();
                document.getElementById('current-time').textContent = now.toLocaleString();
            }}, 1000);
            
            // Function to change city and fetch new weather
            async function changeCity() {{
                const citySelect = document.getElementById('city-select');
                const selectedCity = citySelect.value;
                const loading = document.getElementById('loading');
                const weatherGrid = document.getElementById('weather-grid');
                
                // Show loading indicator
                loading.classList.add('active');
                weatherGrid.classList.add('pulse');
                
                try {{
                    // Fetch weather data for selected city
                    const response = await fetch(`${{window.location.origin}}${{window.location.pathname}}?city=${{selectedCity}}`);
                    const weather = await response.json();
                    
                    // Update city name
                    document.getElementById('city-name').textContent = weather.city;
                    
                    // Update weather information
                    document.getElementById('temperature').textContent = 
                        weather.temperature !== 'N/A' ? `${{weather.temperature}}°F` : 'N/A';
                    document.getElementById('conditions').textContent = 
                        weather.description !== 'Unable to fetch weather' ? 
                        weather.description.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : 
                        'N/A';
                    document.getElementById('humidity').textContent = 
                        weather.humidity !== 'N/A' ? `${{weather.humidity}}%` : 'N/A';
                    
                    // Remove pulse animation after update
                    setTimeout(() => {{
                        weatherGrid.classList.remove('pulse');
                    }}, 1000);
                    
                }} catch (error) {{
                    console.error('Error fetching weather:', error);
                    alert('Failed to fetch weather data. Please try again.');
                }} finally {{
                    // Hide loading indicator
                    loading.classList.remove('active');
                }}
            }}
            
            function selectService(element) {{
                // Remove previous selection
                document.querySelectorAll('.service-card').forEach(card => {{
                    card.classList.remove('selected');
                }});
                
                // Add selection to clicked card
                element.classList.add('selected');
                selectedService = element.getAttribute('data-service');
            }}
            
            async function submitService() {{
                if (!selectedService) {{
                    alert('Please select a service first!');
                    return;
                }}
                
                const responseArea = document.getElementById('response-area');
                const responseText = document.getElementById('response-text');
                
                try {{
                    const response = await fetch(window.location.href, {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            service: selectedService
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    responseText.innerHTML = `
                        <strong>Selected Service:</strong> ${{selectedService.toUpperCase()}}<br>
                        <strong>Status:</strong> Ready to use<br>
                        <strong>Timestamp:</strong> ${{data.timestamp}}<br>
                        <br>
                        <em>Next steps: Configure and integrate this service in your AWS Console.</em>
                    `;
                    
                    responseArea.classList.add('active');
                }} catch (error) {{
                    responseText.innerHTML = `<strong>Error:</strong> ${{error.message}}`;
                    responseArea.classList.add('active');
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return html
