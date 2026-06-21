import os
import sys

def main():
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    app_exists = os.path.exists(os.path.join("backend", "app"))
    weather_impact_exists = os.path.exists(os.path.join("backend", "app", "weather_impact"))
    
    print(f"Whether backend/app exists: {app_exists}")
    print(f"Whether backend/app/weather_impact exists: {weather_impact_exists}")

if __name__ == "__main__":
    main()
