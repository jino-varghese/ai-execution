import json
import boto3
from datetime import datetime
import os

# Initialize AWS Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)

# Model ID for Claude 3 Sonnet on Bedrock
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# RAG Knowledge Base - Destination Data
# This serves as our retrieval database for destination-specific information
DESTINATION_KNOWLEDGE_BASE = {
    "paris": {
        "name": "Paris",
        "country": "France",
        "description": "The City of Light, known for its art, fashion, gastronomy, and culture.",
        "best_time": "April to June and September to October",
        "currency": "EUR",
        "language": "French",
        "attractions": [
            {
                "name": "Eiffel Tower",
                "category": "landmark",
                "description": "Iconic 330-meter iron tower, symbol of Paris. Offers panoramic city views from three observation levels.",
                "time_needed": "2-3 hours",
                "best_time": "Early morning or sunset",
                "avg_cost": "€26-34",
                "location": "Champ de Mars, 7th arrondissement"
            },
            {
                "name": "Louvre Museum",
                "category": "culture",
                "description": "World's largest art museum, home to Mona Lisa and 38,000 artworks spanning 9,000 years.",
                "time_needed": "3-4 hours minimum",
                "best_time": "Wednesday or Friday evenings (less crowded)",
                "avg_cost": "€17",
                "location": "Rue de Rivoli, 1st arrondissement"
            },
            {
                "name": "Notre-Dame Cathedral",
                "category": "culture",
                "description": "Gothic masterpiece from the 12th century. Currently under restoration post-2019 fire.",
                "time_needed": "1-2 hours",
                "best_time": "Morning",
                "avg_cost": "Free (exterior viewing)",
                "location": "Île de la Cité, 4th arrondissement"
            },
            {
                "name": "Versailles Palace",
                "category": "culture",
                "description": "Opulent royal château with stunning gardens, Hall of Mirrors, and rich history.",
                "time_needed": "Half to full day",
                "best_time": "Weekday mornings",
                "avg_cost": "€19.50",
                "location": "Versailles (30 min from Paris)"
            },
            {
                "name": "Montmartre & Sacré-Cœur",
                "category": "culture",
                "description": "Historic hilltop neighborhood with artistic heritage, cobblestone streets, and white basilica.",
                "time_needed": "2-3 hours",
                "best_time": "Late afternoon",
                "avg_cost": "Free",
                "location": "18th arrondissement"
            },
            {
                "name": "Seine River Cruise",
                "category": "relaxation",
                "description": "Scenic boat tour past illuminated monuments and bridges.",
                "time_needed": "1-2 hours",
                "best_time": "Evening (dinner cruise)",
                "avg_cost": "€15-150",
                "location": "Various departure points"
            },
            {
                "name": "Champs-Élysées & Arc de Triomphe",
                "category": "shopping",
                "description": "Famous avenue with luxury shops, cafés, and monumental arch.",
                "time_needed": "2-3 hours",
                "best_time": "Afternoon to evening",
                "avg_cost": "Free (shopping varies)",
                "location": "8th arrondissement"
            },
            {
                "name": "Latin Quarter",
                "category": "food",
                "description": "Historic student district with bookshops, bistros, and Sorbonne University.",
                "time_needed": "2-3 hours",
                "best_time": "Lunch or dinner",
                "avg_cost": "Varies",
                "location": "5th arrondissement"
            }
        ],
        "dining": {
            "budget": ["Crêperies", "Boulangeries", "Street markets", "Bistros"],
            "moderate": ["Traditional brasseries", "Wine bars", "Café restaurants"],
            "luxury": ["Michelin-starred restaurants", "Le Jules Verne (Eiffel Tower)", "L'Ambroisie"]
        },
        "local_cuisine": ["Croissants", "Escargots", "Coq au vin", "Crème brûlée", "French onion soup", "Macarons"],
        "transportation": {
            "metro": "Excellent coverage, buy Paris Visite pass",
            "walking": "Very walkable, especially central areas",
            "bike": "Vélib bike-sharing available",
            "taxi": "Available but expensive"
        },
        "tips": [
            "Learn basic French phrases - locals appreciate the effort",
            "Book major attractions online in advance",
            "Metro is fastest way to get around",
            "Many museums free on first Sunday of month",
            "Pickpockets common in tourist areas - stay vigilant"
        ],
        "budget_estimate": {
            "budget": "€80-120/day",
            "moderate": "€200-350/day",
            "luxury": "€500+/day"
        }
    },
    "tokyo": {
        "name": "Tokyo",
        "country": "Japan",
        "description": "Ultra-modern metropolis blending traditional temples with neon-lit skyscrapers and cutting-edge technology.",
        "best_time": "March to May (cherry blossoms) and September to November",
        "currency": "JPY",
        "language": "Japanese",
        "attractions": [
            {
                "name": "Senso-ji Temple",
                "category": "culture",
                "description": "Tokyo's oldest Buddhist temple in Asakusa, with iconic Thunder Gate and shopping street.",
                "time_needed": "2 hours",
                "best_time": "Early morning (6 AM) before crowds",
                "avg_cost": "Free",
                "location": "Asakusa"
            },
            {
                "name": "Tokyo Skytree",
                "category": "landmark",
                "description": "634-meter broadcasting tower with observation decks offering 360° city views.",
                "time_needed": "2-3 hours",
                "best_time": "Sunset",
                "avg_cost": "¥2,100-3,100",
                "location": "Sumida"
            },
            {
                "name": "Shibuya Crossing",
                "category": "culture",
                "description": "World's busiest pedestrian crossing, emblematic of Tokyo's energy.",
                "time_needed": "1 hour",
                "best_time": "Evening when illuminated",
                "avg_cost": "Free",
                "location": "Shibuya"
            },
            {
                "name": "Tsukiji Outer Market",
                "category": "food",
                "description": "Famous seafood market with fresh sushi, street food, and culinary tools.",
                "time_needed": "2-3 hours",
                "best_time": "Early morning (6-8 AM)",
                "avg_cost": "¥2,000-5,000 for food",
                "location": "Chuo"
            },
            {
                "name": "Meiji Shrine",
                "category": "culture",
                "description": "Serene Shinto shrine in forested grounds, dedicated to Emperor Meiji.",
                "time_needed": "1-2 hours",
                "best_time": "Morning",
                "avg_cost": "Free",
                "location": "Shibuya"
            },
            {
                "name": "Akihabara",
                "category": "shopping",
                "description": "Electric Town - hub for anime, manga, electronics, and otaku culture.",
                "time_needed": "3-4 hours",
                "best_time": "Afternoon to evening",
                "avg_cost": "Varies",
                "location": "Chiyoda"
            },
            {
                "name": "Mount Fuji Day Trip",
                "category": "nature",
                "description": "Japan's iconic volcano, visible from observation decks or via day tour.",
                "time_needed": "Full day",
                "best_time": "Clear winter days",
                "avg_cost": "¥8,000-15,000",
                "location": "Yamanashi Prefecture"
            },
            {
                "name": "Ueno Park",
                "category": "nature",
                "description": "Large public park with museums, zoo, and stunning cherry blossoms.",
                "time_needed": "2-3 hours",
                "best_time": "Spring (cherry blossom season)",
                "avg_cost": "Free (museums extra)",
                "location": "Taito"
            }
        ],
        "dining": {
            "budget": ["Ramen shops", "Conveyor belt sushi", "7-Eleven bentos", "Standing bars"],
            "moderate": ["Izakayas", "Tonkatsu restaurants", "Traditional kaiseki (entry-level)"],
            "luxury": ["Sukiyabashi Jiro", "Michelin-starred kaiseki", "High-end teppanyaki"]
        },
        "local_cuisine": ["Sushi", "Ramen", "Tempura", "Tonkatsu", "Yakitori", "Okonomiyaki", "Matcha desserts"],
        "transportation": {
            "rail": "Extensive JR and metro network - get JR Pass for tourists",
            "walking": "Very walkable, each neighborhood distinct",
            "taxi": "Clean but expensive",
            "IC_card": "Get Suica or Pasmo card for easy transit"
        },
        "tips": [
            "Download Google Translate with offline Japanese",
            "Cash is king - many places don't accept cards",
            "Remove shoes when entering homes and some restaurants",
            "Don't eat while walking",
            "Bow when greeting",
            "Tattoos may be prohibited in public baths"
        ],
        "budget_estimate": {
            "budget": "€80-120/day",
            "moderate": "€150-300/day",
            "luxury": "€500+/day"
        }
    },
    "bali": {
        "name": "Bali",
        "country": "Indonesia",
        "description": "Tropical paradise with stunning beaches, terraced rice paddies, spiritual temples, and wellness culture.",
        "best_time": "April to October (dry season)",
        "currency": "IDR",
        "language": "Indonesian, Balinese",
        "attractions": [
            {
                "name": "Ubud Monkey Forest",
                "category": "nature",
                "description": "Sacred sanctuary with 700+ Balinese macaques, ancient temples, and lush jungle.",
                "time_needed": "2 hours",
                "best_time": "Early morning",
                "avg_cost": "IDR 80,000",
                "location": "Ubud"
            },
            {
                "name": "Tanah Lot Temple",
                "category": "culture",
                "description": "Iconic sea temple on offshore rock formation, spectacular sunset views.",
                "time_needed": "2 hours",
                "best_time": "Sunset",
                "avg_cost": "IDR 60,000",
                "location": "Tabanan Regency"
            },
            {
                "name": "Tegallalang Rice Terraces",
                "category": "nature",
                "description": "UNESCO-heritage rice paddies with dramatic stepped landscapes.",
                "time_needed": "2-3 hours",
                "best_time": "Morning light",
                "avg_cost": "IDR 15,000 donation",
                "location": "Ubud"
            },
            {
                "name": "Seminyak Beach",
                "category": "relaxation",
                "description": "Upscale beach area with beach clubs, surfing, and sunsets.",
                "time_needed": "Half day",
                "best_time": "Afternoon/sunset",
                "avg_cost": "Free (beach clubs vary)",
                "location": "Seminyak"
            },
            {
                "name": "Tirta Empul Water Temple",
                "category": "culture",
                "description": "Holy spring water temple where locals perform purification rituals.",
                "time_needed": "2-3 hours",
                "best_time": "Morning",
                "avg_cost": "IDR 50,000",
                "location": "Tampaksiring"
            },
            {
                "name": "Mount Batur Sunrise Trek",
                "category": "adventure",
                "description": "Active volcano trek starting at 3 AM for breathtaking sunrise views.",
                "time_needed": "6-7 hours",
                "best_time": "Early morning start",
                "avg_cost": "IDR 500,000-750,000",
                "location": "Kintamani"
            },
            {
                "name": "Spa & Wellness Retreat",
                "category": "relaxation",
                "description": "Traditional Balinese massage, yoga retreats, and holistic healing.",
                "time_needed": "2-4 hours",
                "best_time": "Anytime",
                "avg_cost": "IDR 200,000-2,000,000",
                "location": "Ubud, Seminyak"
            },
            {
                "name": "Nusa Penida Island",
                "category": "adventure",
                "description": "Dramatic cliffs, crystal-clear waters, manta rays, and Instagram-famous spots.",
                "time_needed": "Full day",
                "best_time": "Dry season",
                "avg_cost": "IDR 800,000-1,500,000",
                "location": "Off Bali's coast"
            }
        ],
        "dining": {
            "budget": ["Warungs", "Street food", "Local markets", "Nasi goreng stalls"],
            "moderate": ["Beachfront restaurants", "Ubud organic cafés", "Indonesian restaurants"],
            "luxury": ["Locavore", "Mozaic", "Resort fine dining"]
        },
        "local_cuisine": ["Nasi goreng", "Satay", "Babi guling", "Lawar", "Rendang", "Pisang goreng"],
        "transportation": {
            "scooter": "Most popular - rent for IDR 50,000/day (need license)",
            "driver": "Hire private driver for full day (IDR 500,000-700,000)",
            "taxi": "Bluebird taxis or Grab/Gojek apps",
            "walking": "Limited to small areas like Ubud center"
        },
        "tips": [
            "Dress modestly at temples - sarong required",
            "Bargain at markets (except fixed-price shops)",
            "Drink bottled water only",
            "Be cautious of monkeys - they steal belongings",
            "Respect ceremonies and offerings on streets",
            "Beware of scooter rental scams - check bike thoroughly"
        ],
        "budget_estimate": {
            "budget": "€30-60/day",
            "moderate": "€100-200/day",
            "luxury": "€400+/day"
        }
    },
    "new york": {
        "name": "New York City",
        "country": "United States",
        "description": "The city that never sleeps - global hub of culture, finance, fashion, and entertainment.",
        "best_time": "April to June and September to November",
        "currency": "USD",
        "language": "English",
        "attractions": [
            {
                "name": "Statue of Liberty & Ellis Island",
                "category": "landmark",
                "description": "Iconic symbol of freedom with museum and immigration history.",
                "time_needed": "3-4 hours",
                "best_time": "Morning (book tickets weeks in advance)",
                "avg_cost": "$24-30",
                "location": "New York Harbor"
            },
            {
                "name": "Central Park",
                "category": "nature",
                "description": "843-acre urban oasis with lakes, meadows, and cultural attractions.",
                "time_needed": "2-4 hours",
                "best_time": "Morning or late afternoon",
                "avg_cost": "Free",
                "location": "Manhattan"
            },
            {
                "name": "Metropolitan Museum of Art",
                "category": "culture",
                "description": "One of world's finest art museums with 5,000 years of art from around the globe.",
                "time_needed": "3-4 hours minimum",
                "best_time": "Weekday mornings",
                "avg_cost": "$30",
                "location": "Upper East Side"
            },
            {
                "name": "Times Square",
                "category": "landmark",
                "description": "Bright lights, Broadway theaters, and quintessential NYC energy.",
                "time_needed": "1-2 hours",
                "best_time": "Evening when lit up",
                "avg_cost": "Free",
                "location": "Midtown Manhattan"
            },
            {
                "name": "Brooklyn Bridge",
                "category": "landmark",
                "description": "Historic suspension bridge with pedestrian walkway and Manhattan skyline views.",
                "time_needed": "1-2 hours",
                "best_time": "Sunrise or sunset",
                "avg_cost": "Free",
                "location": "Connects Manhattan and Brooklyn"
            },
            {
                "name": "Broadway Show",
                "category": "culture",
                "description": "World-class theater productions in iconic venues.",
                "time_needed": "3 hours",
                "best_time": "Evening performances",
                "avg_cost": "$80-400+",
                "location": "Theater District"
            },
            {
                "name": "Fifth Avenue Shopping",
                "category": "shopping",
                "description": "Luxury flagship stores from Apple to Tiffany & Co.",
                "time_needed": "3-4 hours",
                "best_time": "Weekday afternoons",
                "avg_cost": "Varies widely",
                "location": "Midtown Manhattan"
            },
            {
                "name": "High Line Park",
                "category": "nature",
                "description": "Elevated park on historic freight rail line with gardens and city views.",
                "time_needed": "1-2 hours",
                "best_time": "Late afternoon",
                "avg_cost": "Free",
                "location": "Chelsea/Meatpacking District"
            }
        ],
        "dining": {
            "budget": ["Dollar pizza slices", "Food trucks", "Delis", "Halal carts"],
            "moderate": ["Italian restaurants", "Steakhouses", "Ethnic neighborhoods", "Brunch spots"],
            "luxury": ["Per Se", "Eleven Madison Park", "Le Bernardin", "Michelin-starred restaurants"]
        },
        "local_cuisine": ["New York pizza", "Bagels with lox", "Pastrami on rye", "Hot dogs", "Cheesecake", "Black and white cookies"],
        "transportation": {
            "subway": "24/7 service, get MetroCard or contactless payment",
            "walking": "Very walkable, especially Manhattan",
            "taxi": "Yellow cabs abundant, or use Uber/Lyft",
            "bus": "Slower but scenic"
        },
        "tips": [
            "Walk on right, stand right on escalators",
            "Tipping expected: 18-20% at restaurants",
            "Get MetroCard unlimited for multi-day stays",
            "Book Broadway tickets via TKTS booth for discounts",
            "Avoid Times Square restaurants - overpriced tourist traps",
            "Use CityMapper app for navigation"
        ],
        "budget_estimate": {
            "budget": "€120-200/day",
            "moderate": "€300-500/day",
            "luxury": "€700+/day"
        }
    }
}


def lambda_handler(event, context):
    """
    AWS Lambda handler for AI-powered travel itinerary generation using Amazon Bedrock
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)

        # Extract parameters
        destination = body.get('destination', '').strip()
        duration = int(body.get('duration', 5))
        budget = body.get('budget', 'moderate')
        interests = body.get('interests', [])
        travel_style = body.get('travelStyle', 'solo')
        preferences = body.get('preferences', '')

        print(f"Generating itinerary for {destination}, {duration} days, {budget} budget")

        # Generate itinerary using Bedrock LLM with RAG
        itinerary = generate_ai_itinerary(
            destination=destination,
            duration=duration,
            budget=budget,
            interests=interests,
            travel_style=travel_style,
            preferences=preferences
        )

        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'itinerary': itinerary,
                'generated_at': datetime.utcnow().isoformat(),
                'powered_by': 'Amazon Bedrock (Claude 3 Sonnet)'
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


def retrieve_destination_knowledge(destination):
    """
    RAG Retrieval: Fetch relevant destination information from knowledge base
    This simulates a vector database retrieval based on destination
    """
    dest_key = destination.lower().strip()

    # Try exact match first
    if dest_key in DESTINATION_KNOWLEDGE_BASE:
        return DESTINATION_KNOWLEDGE_BASE[dest_key]

    # Try partial matching
    for key, data in DESTINATION_KNOWLEDGE_BASE.items():
        if dest_key in key or key in dest_key:
            return data
        if dest_key in data['name'].lower():
            return data

    # Return None if not found - LLM will use general knowledge
    return None


def filter_attractions_by_interests(attractions, interests):
    """
    Filter attractions based on user interests for better personalization
    """
    if not interests or not attractions:
        return attractions

    # Score attractions based on interest matching
    scored_attractions = []
    for attraction in attractions:
        score = 0
        attraction_category = attraction.get('category', '').lower()

        # Check if attraction category matches any user interest
        for interest in interests:
            if interest.lower() in attraction_category or attraction_category in interest.lower():
                score += 2
            # Partial matches
            if interest.lower() in attraction.get('description', '').lower():
                score += 1

        scored_attractions.append((score, attraction))

    # Sort by score (highest first) and return
    scored_attractions.sort(key=lambda x: x[0], reverse=True)

    # Return attractions with score > 0, or all if none match
    filtered = [att for score, att in scored_attractions if score > 0]
    return filtered if filtered else attractions


def build_llm_prompt(destination, duration, budget, interests, travel_style, preferences, knowledge):
    """
    Build comprehensive prompt for LLM with RAG context
    This implements the "fine-tuned" behavior through prompt engineering
    """

    # Build context from RAG knowledge
    context = ""
    if knowledge:
        context = f"""
DESTINATION KNOWLEDGE BASE:
Destination: {knowledge['name']}, {knowledge['country']}
Description: {knowledge['description']}
Best Time to Visit: {knowledge['best_time']}
Currency: {knowledge['currency']}
Language: {knowledge['language']}

ATTRACTIONS DATABASE:
"""
        # Add filtered attractions based on interests
        filtered_attractions = filter_attractions_by_interests(knowledge['attractions'], interests)
        for att in filtered_attractions[:10]:  # Limit to top 10 to save tokens
            context += f"""
- {att['name']} ({att['category']})
  Description: {att['description']}
  Time Needed: {att['time_needed']}
  Best Time: {att['best_time']}
  Location: {att['location']}
  Cost: {att['avg_cost']}
"""

        context += f"""
DINING OPTIONS ({budget} budget):
{', '.join(knowledge['dining'].get(budget, knowledge['dining']['moderate']))}

LOCAL CUISINE TO TRY:
{', '.join(knowledge['local_cuisine'])}

TRANSPORTATION:
"""
        for mode, info in knowledge['transportation'].items():
            context += f"- {mode.replace('_', ' ').title()}: {info}\n"

        context += f"""
TRAVEL TIPS:
"""
        for tip in knowledge['tips']:
            context += f"- {tip}\n"

        context += f"""
BUDGET ESTIMATE:
{budget.title()} Budget: {knowledge['budget_estimate'].get(budget, knowledge['budget_estimate']['moderate'])} per person
"""

    # Build the main prompt
    prompt = f"""You are an expert travel advisor AI with deep knowledge of destinations worldwide. Your task is to create a highly personalized, detailed travel itinerary.

USER PREFERENCES:
- Destination: {destination}
- Duration: {duration} days
- Budget Level: {budget}
- Travel Style: {travel_style}
- Interests: {', '.join(interests) if interests else 'General sightseeing'}
- Additional Preferences: {preferences if preferences else 'None specified'}

{context}

INSTRUCTIONS:
Create a detailed {duration}-day itinerary that:
1. Matches the user's {budget} budget level
2. Focuses heavily on their interests: {', '.join(interests) if interests else 'balanced activities'}
3. Suits {travel_style} travelers
4. Includes specific attractions, restaurants, and experiences from the knowledge base above
5. Provides realistic time estimates and practical tips
6. Balances must-see landmarks with authentic local experiences
7. Accounts for travel time between locations
8. Suggests specific restaurants and dining experiences matching the budget
9. Includes insider tips and best times to visit attractions

OUTPUT FORMAT (JSON):
Return ONLY a valid JSON object with this exact structure (no markdown, no explanations, just JSON):
{{
  "destination": "{destination}",
  "duration": {duration},
  "budget": "{budget}",
  "summary": "A compelling 2-3 sentence overview of the trip",
  "days": [
    {{
      "day": 1,
      "title": "Brief day theme",
      "activities": [
        {{
          "time": "Morning/Afternoon/Evening",
          "activity": "Specific activity name",
          "description": "Detailed description with practical tips, costs, and insider advice"
        }}
      ]
    }}
  ],
  "tips": "Overall trip tips and recommendations",
  "estimated_total_cost": "Cost range for the entire trip"
}}

Be specific, creative, and ensure the itinerary feels authentic and well-researched. Use the knowledge base above for accuracy."""

    return prompt


def generate_ai_itinerary(destination, duration, budget, interests, travel_style, preferences):
    """
    Generate personalized travel itinerary using Amazon Bedrock LLM with RAG

    This implements:
    1. RAG (Retrieval Augmented Generation) - retrieves destination knowledge
    2. LLM-powered generation - uses Claude via Bedrock
    3. Agent behavior - personalization based on user preferences
    """

    # Step 1: RAG Retrieval - Get destination knowledge
    knowledge = retrieve_destination_knowledge(destination)

    # Step 2: Build prompt with retrieved knowledge
    prompt = build_llm_prompt(
        destination=destination,
        duration=duration,
        budget=budget,
        interests=interests,
        travel_style=travel_style,
        preferences=preferences,
        knowledge=knowledge
    )

    # Step 3: Call Amazon Bedrock LLM
    try:
        # Prepare request for Claude 3 on Bedrock
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Invoke Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )

        # Parse response
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']

        # Extract JSON from response (in case LLM added extra text)
        ai_response = ai_response.strip()
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]
        if ai_response.startswith('```'):
            ai_response = ai_response[3:]
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]
        ai_response = ai_response.strip()

        # Parse JSON response
        itinerary = json.loads(ai_response)

        # Add metadata
        itinerary['ai_generated'] = True
        itinerary['model'] = 'Amazon Bedrock - Claude 3 Sonnet'
        itinerary['knowledge_source'] = 'RAG' if knowledge else 'LLM General Knowledge'

        return itinerary

    except Exception as e:
        print(f"Bedrock API error: {str(e)}")
        # Fallback to basic itinerary if Bedrock fails
        return generate_fallback_itinerary(destination, duration, budget, interests, travel_style, knowledge)


def generate_fallback_itinerary(destination, duration, budget, interests, travel_style, knowledge):
    """
    Fallback itinerary generation if Bedrock is unavailable
    Uses template-based generation with RAG knowledge
    """

    if not knowledge:
        dest_name = destination.title()
        summary = f"A {duration}-day {budget} adventure in {dest_name} for {travel_style} travelers."
        tips = "Research local customs and weather before your trip."
        activities_pool = [
            {"time": "Morning", "activity": "Explore main attractions", "description": "Visit popular landmarks and sites"},
            {"time": "Afternoon", "activity": "Local dining experience", "description": "Try authentic local cuisine"},
            {"time": "Evening", "activity": "Evening leisure", "description": "Relax and enjoy the nightlife"}
        ]
    else:
        dest_name = knowledge['name']
        summary = f"A {duration}-day {budget} adventure in {dest_name}, {knowledge['country']}. {knowledge['description']}"
        tips = " ".join(knowledge['tips'][:3])

        # Build activities from knowledge base
        filtered_attractions = filter_attractions_by_interests(knowledge['attractions'], interests)
        activities_pool = []
        for att in filtered_attractions:
            activities_pool.append({
                "time": "Morning" if "morning" in att['best_time'].lower() else "Afternoon",
                "activity": f"Visit {att['name']}",
                "description": f"{att['description']} Time needed: {att['time_needed']}. Cost: {att['avg_cost']}"
            })

    # Generate days
    days = []
    for day_num in range(1, duration + 1):
        if day_num == 1:
            day_title = "Arrival & Orientation"
            activities = [
                {"time": "Morning", "activity": f"Arrive in {dest_name}", "description": "Check into accommodation and freshen up"},
                {"time": "Afternoon", "activity": "Neighborhood exploration", "description": "Get oriented with a walking tour"},
                {"time": "Evening", "activity": "Welcome dinner", "description": "Sample local cuisine"}
            ]
        elif day_num == duration:
            day_title = "Departure Day"
            activities = [
                {"time": "Morning", "activity": "Last-minute activities", "description": "Final exploration or souvenir shopping"},
                {"time": "Afternoon", "activity": f"Depart {dest_name}", "description": "Check out and travel to airport"}
            ]
        else:
            day_title = f"Day {day_num} Exploration"
            # Select 3 random activities
            import random
            selected = random.sample(activities_pool, min(3, len(activities_pool)))
            activities = selected

        days.append({
            "day": day_num,
            "title": day_title,
            "activities": activities
        })

    return {
        "destination": dest_name,
        "duration": duration,
        "budget": budget,
        "summary": summary,
        "days": days,
        "tips": tips,
        "estimated_total_cost": knowledge['budget_estimate'][budget] if knowledge else f"${100 * duration}-${200 * duration}",
        "ai_generated": False,
        "model": "Fallback Template",
        "knowledge_source": "RAG" if knowledge else "Template"
    }


# For local testing
if __name__ == '__main__':
    # Test with sample data
    test_event = {
        'body': json.dumps({
            'destination': 'Paris',
            'duration': 5,
            'budget': 'moderate',
            'interests': ['culture', 'food'],
            'travelStyle': 'couple',
            'preferences': 'romantic experiences, avoid crowds'
        })
    }

    # Note: This will fail locally without AWS credentials
    # Use fallback for local testing
    print("Testing fallback itinerary generation...")
    knowledge = retrieve_destination_knowledge('Paris')
    result = generate_fallback_itinerary('Paris', 5, 'moderate', ['culture', 'food'], 'couple', knowledge)
    print(json.dumps(result, indent=2))
