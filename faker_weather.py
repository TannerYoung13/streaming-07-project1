import faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = faker.Faker()

# Function to generate temperature data for each hour
def generate_hourly_temperatures():
    hourly_temperatures = []
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for hour in range(24):
        timestamp = base_date + timedelta(hours=hour)
        temperature = round(random.uniform(-10, 35), 2)  # Random temperature in Celsius
        
        hourly_temperatures.append({
            'timestamp': timestamp,
            'temperature': temperature,
        })

    return hourly_temperatures

# Generate and print the hourly temperatures
hourly_temperatures = generate_hourly_temperatures()
for entry in hourly_temperatures:
    print(f"Time: {entry['timestamp']}, Temperature: {entry['temperature']}°C")

# Formating
