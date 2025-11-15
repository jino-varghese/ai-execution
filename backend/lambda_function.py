import json
import random
from datetime import datetime

# Sample destination data (simulating RAG database)
DESTINATION_DATA = {
    "paris": {
        "name": "Paris",
        "attractions": [
            {"name": "Eiffel Tower", "type": "landmark", "time": "2-3 hours"},
            {"name": "Louvre Museum", "type": "culture", "time": "3-4 hours"},
            {"name": "Notre-Dame Cathedral", "type": "culture", "time": "1-2 hours"},
            {"name": "Champs-Élysées", "type": "shopping", "time": "2-3 hours"},
            {"name": "Montmartre & Sacré-Cœur", "type": "culture", "time": "2-3 hours"},
            {"name": "Seine River Cruise", "type": "relaxation", "time": "1-2 hours"},
            {"name": "Versailles Palace", "type": "culture", "time": "4-5 hours"},
            {"name": "Latin Quarter", "type": "food", "time": "2-3 hours"}
        ],
        "food": ["French bistro", "Michelin-starred restaurant", "Café", "Patisserie"],
        "tips": "Best visited in spring or fall. Metro is the easiest way to get around."
    },
    "tokyo": {
        "name": "Tokyo",
        "attractions": [
            {"name": "Senso-ji Temple", "type": "culture", "time": "2 hours"},
            {"name": "Tokyo Skytree", "type": "landmark", "time": "2-3 hours"},
            {"name": "Shibuya Crossing", "type": "culture", "time": "1 hour"},
            {"name": "Tsukiji Outer Market", "type": "food", "time": "2-3 hours"},
            {"name": "Meiji Shrine", "type": "culture", "time": "1-2 hours"},
            {"name": "Akihabara", "type": "shopping", "time": "3-4 hours"},
            {"name": "Mount Fuji Day Trip", "type": "nature", "time": "Full day"},
            {"name": "Ueno Park", "type": "nature", "time": "2-3 hours"}
        ],
        "food": ["Sushi restaurant", "Ramen shop", "Izakaya", "Tempura restaurant"],
        "tips": "Get a JR Pass for train travel. Learn basic Japanese phrases."
    },
    "new york": {
        "name": "New York",
        "attractions": [
            {"name": "Statue of Liberty", "type": "landmark", "time": "3-4 hours"},
            {"name": "Central Park", "type": "nature", "time": "2-4 hours"},
            {"name": "Metropolitan Museum of Art", "type": "culture", "time": "3-4 hours"},
            {"name": "Times Square", "type": "landmark", "time": "1-2 hours"},
            {"name": "Brooklyn Bridge", "type": "landmark", "time": "1-2 hours"},
            {"name": "Broadway Show", "type": "culture", "time": "3 hours"},
            {"name": "Fifth Avenue Shopping", "type": "shopping", "time": "3-4 hours"},
            {"name": "High Line Park", "type": "nature", "time": "1-2 hours"}
        ],
        "food": ["New York pizza", "Fine dining", "Food hall", "Deli"],
        "tips": "Use the subway for transportation. Book Broadway shows in advance."
    },
    "bali": {
        "name": "Bali",
        "attractions": [
            {"name": "Ubud Monkey Forest", "type": "nature", "time": "2 hours"},
            {"name": "Tanah Lot Temple", "type": "culture", "time": "2 hours"},
            {"name": "Rice Terraces", "type": "nature", "time": "2-3 hours"},
            {"name": "Beaches (Seminyak, Nusa Dua)", "type": "relaxation", "time": "4-6 hours"},
            {"name": "Water Temple (Tirta Empul)", "type": "culture", "time": "2-3 hours"},
            {"name": "Surfing Lessons", "type": "adventure", "time": "2-3 hours"},
            {"name": "Spa & Wellness", "type": "relaxation", "time": "2-3 hours"},
            {"name": "Mount Batur Sunrise Trek", "type": "adventure", "time": "6-7 hours"}
        ],
        "food": ["Balinese warung", "Seafood restaurant", "Healthy café", "Traditional feast"],
        "tips": "Rent a scooter for flexibility. Visit temples with proper attire."
    }
}

def lambda_handler(event, context):
    """
    AWS Lambda handler for travel itinerary generation
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)

        # Extract parameters
        destination = body.get('destination', '').lower().strip()
        duration = int(body.get('duration', 5))
        budget = body.get('budget', 'moderate')
        interests = body.get('interests', [])
        travel_style = body.get('travelStyle', 'solo')
        preferences = body.get('preferences', '')

        # Generate itinerary
        itinerary = generate_itinerary(
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
                'generated_at': datetime.utcnow().isoformat()
            })
        }

    except Exception as e:
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

def generate_itinerary(destination, duration, budget, interests, travel_style, preferences):
    """
    Generate personalized travel itinerary based on user preferences
    This is a simplified implementation. In production, this would use:
    - Fine-tuned LLM for natural language generation
    - RAG system for real-time destination information
    - AI agent for optimization and personalization
    """

    # Get destination data or use generic
    dest_key = destination.lower()
    dest_info = DESTINATION_DATA.get(dest_key, create_generic_destination(destination))

    # Filter attractions by interests
    filtered_attractions = filter_attractions_by_interests(
        dest_info['attractions'],
        interests
    )

    # Generate daily itinerary
    days = []
    for day_num in range(1, duration + 1):
        day_plan = generate_day_plan(
            day_num=day_num,
            total_days=duration,
            attractions=filtered_attractions,
            interests=interests,
            budget=budget,
            travel_style=travel_style,
            dest_info=dest_info
        )
        days.append(day_plan)

    # Create summary
    summary = create_summary(
        destination=dest_info['name'],
        duration=duration,
        budget=budget,
        interests=interests,
        travel_style=travel_style
    )

    return {
        'destination': dest_info['name'],
        'duration': duration,
        'budget': budget,
        'summary': summary,
        'days': days,
        'tips': dest_info.get('tips', 'Research local customs and weather before your trip.')
    }

def filter_attractions_by_interests(attractions, interests):
    """Filter attractions based on user interests"""
    if not interests:
        return attractions

    filtered = [a for a in attractions if a.get('type') in interests]

    # If no matches, return all attractions
    return filtered if filtered else attractions

def generate_day_plan(day_num, total_days, attractions, interests, budget, travel_style, dest_info):
    """Generate activities for a specific day"""
    activities = []

    if day_num == 1:
        # Arrival day
        activities = [
            {
                'time': 'Morning',
                'activity': f'Arrive in {dest_info["name"]}',
                'description': 'Check into accommodation and freshen up'
            },
            {
                'time': 'Afternoon',
                'activity': 'Neighborhood exploration',
                'description': 'Take a walking tour to get oriented with the area'
            },
            {
                'time': 'Evening',
                'activity': f'Welcome dinner at {random.choice(dest_info["food"])}',
                'description': 'Sample local cuisine and relax after journey'
            }
        ]
    elif day_num == total_days:
        # Departure day
        activities = [
            {
                'time': 'Morning',
                'activity': 'Final exploration and shopping',
                'description': 'Pick up any last-minute souvenirs'
            },
            {
                'time': 'Afternoon',
                'activity': f'Departure from {dest_info["name"]}',
                'description': 'Check out and travel to airport'
            }
        ]
    else:
        # Regular day - select attractions
        day_attractions = random.sample(
            attractions,
            min(2, len(attractions))
        )

        for i, attraction in enumerate(day_attractions):
            time_of_day = 'Morning' if i == 0 else 'Afternoon'
            activities.append({
                'time': time_of_day,
                'activity': f'Visit {attraction["name"]}',
                'description': f'Recommended time: {attraction.get("time", "2-3 hours")}'
            })

        # Add meal
        restaurant_type = get_restaurant_by_budget(budget, dest_info['food'])
        activities.append({
            'time': 'Evening',
            'activity': f'Dinner at {restaurant_type}',
            'description': 'Experience local flavors'
        })

    return {
        'day': day_num,
        'activities': activities
    }

def get_restaurant_by_budget(budget, food_options):
    """Select restaurant type based on budget"""
    if budget == 'luxury':
        return food_options[0] if len(food_options) > 0 else 'fine dining restaurant'
    elif budget == 'budget':
        return food_options[-1] if len(food_options) > 0 else 'local eatery'
    else:
        return random.choice(food_options) if food_options else 'popular restaurant'

def create_summary(destination, duration, budget, interests, travel_style):
    """Create trip summary"""
    interest_str = ', '.join(interests) if interests else 'various activities'

    return (
        f"A {duration}-day {budget} adventure in {destination}, "
        f"perfectly tailored for {travel_style} travelers. "
        f"This itinerary focuses on {interest_str} and includes a balanced mix "
        f"of must-see attractions, local experiences, and leisure time."
    )

def create_generic_destination(destination):
    """Create generic destination data for unknown locations"""
    return {
        'name': destination.title(),
        'attractions': [
            {'name': 'Main attractions tour', 'type': 'culture', 'time': '3-4 hours'},
            {'name': 'Local markets', 'type': 'shopping', 'time': '2-3 hours'},
            {'name': 'Cultural sites', 'type': 'culture', 'time': '2-3 hours'},
            {'name': 'Nature spots', 'type': 'nature', 'time': '2-3 hours'},
            {'name': 'Food tour', 'type': 'food', 'time': '2-3 hours'}
        ],
        'food': ['Local restaurant', 'Street food', 'Traditional cuisine', 'Café'],
        'tips': 'Research local customs, weather, and transportation options.'
    }

# For local testing
if __name__ == '__main__':
    test_event = {
        'body': json.dumps({
            'destination': 'Paris',
            'duration': 5,
            'budget': 'moderate',
            'interests': ['culture', 'food'],
            'travelStyle': 'couple',
            'preferences': 'romantic experiences'
        })
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(json.loads(result['body']), indent=2))
