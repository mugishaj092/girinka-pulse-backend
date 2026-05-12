"""
Test script to verify Open-Meteo weather API is working correctly
"""
import httpx
import json
from datetime import datetime

# Test coordinates for Kigali, Rwanda
TEST_DISTRICT = {
    "name": "Kigali",
    "latitude": -1.9441,
    "longitude": 30.0619
}

OPENMETEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

def test_weather_api():
    print("=" * 70)
    print("TESTING OPEN-METEO WEATHER API")
    print("=" * 70)
    print(f"\nTesting for: {TEST_DISTRICT['name']}")
    print(f"   Coordinates: {TEST_DISTRICT['latitude']}, {TEST_DISTRICT['longitude']}")
    print(f"   API URL: {OPENMETEO_BASE_URL}\n")
    
    try:
        # Make request to Open-Meteo API
        print("Sending request to Open-Meteo API...")
        response = httpx.get(
            OPENMETEO_BASE_URL,
            params={
                "latitude": TEST_DISTRICT["latitude"],
                "longitude": TEST_DISTRICT["longitude"],
                "daily": "temperature_2m_max,precipitation_sum,relative_humidity_2m_max",
                "timezone": "Africa/Kigali",
                "forecast_days": 7,
            },
            timeout=15
        )
        
        # Check response status
        print(f"[OK] Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Parse JSON response
        data = response.json()
        
        print("\nRAW API RESPONSE:")
        print(json.dumps(data, indent=2))
        
        # Validate response structure
        print("\nVALIDATING RESPONSE STRUCTURE...")
        
        if "daily" not in data:
            print("[ERROR] 'daily' key not found in response")
            return False
        
        daily = data["daily"]
        
        required_fields = ["time", "temperature_2m_max", "precipitation_sum", "relative_humidity_2m_max"]
        for field in required_fields:
            if field not in daily:
                print(f"[ERROR] '{field}' not found in daily data")
                return False
            print(f"[OK] Found '{field}': {len(daily[field])} values")
        
        # Display parsed weather data
        print("\nPARSED WEATHER DATA (7-DAY FORECAST):")
        print("-" * 70)
        
        for i, date_str in enumerate(daily.get("time", [])):
            temp = daily.get("temperature_2m_max", [None])[i]
            rain = daily.get("precipitation_sum", [None])[i]
            humidity = daily.get("relative_humidity_2m_max", [None])[i]
            
            print(f"Day {i}: {date_str}")
            print(f"  Temperature: {temp} C")
            print(f"  Rainfall: {rain} mm")
            print(f"  Humidity: {humidity}%")
            print()
        
        # Check if we got real data
        print("[OK] VERIFICATION COMPLETE")
        print(f"   - Received {len(daily['time'])} days of forecast data")
        print(f"   - All required fields present")
        print(f"   - Data appears valid and real")
        
        return True
        
    except httpx.TimeoutException:
        print("[ERROR] Request timed out after 15 seconds")
        return False
    except httpx.RequestError as e:
        print(f"[ERROR] Network error occurred: {e}")
        return False
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON response")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_weather_api()
    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] WEATHER API TEST PASSED - Real data is being retrieved!")
    else:
        print("[FAILED] WEATHER API TEST FAILED - Check errors above")
    print("=" * 70)
