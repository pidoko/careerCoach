import openai
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch API key securely from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set!")

client = openai.OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert career coach specializing in behavioral interview preparation.
You will generate synthetic interview questions, realistic candidate responses, 
and constructive feedback that helps candidates improve.
Candidates are specifically computer science graduate students in Vancouver, BC, and some are neurodivergent.
"""

def generate_interview_data():
    prompt = """
Generate a synthetic interview data point for a behavioral interview.
Include:
- A realistic interview question.
- A high-quality candidate response.
- Detailed, actionable feedback from a hiring manager’s perspective.

Format the output as JSON with the following fields:
{
    "question": "...",
    "response": "...",
    "feedback": "..."
}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use gpt-4-turbo if needed
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)

def safe_generate_interview_data(retries=3):
    for attempt in range(retries):
        try:
            print(f"Generating synthetic data (attempt {attempt + 1})...")
            return generate_interview_data()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait before retrying
    raise Exception("Failed to generate data after several retries.")

# Ensure the data folder exists
output_dir = os.path.join(os.path.dirname(__file__), '../data')
os.makedirs(output_dir, exist_ok=True)

# Create a timestamped filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = os.path.join(output_dir, f'synthetic_interview_data_{timestamp}.jsonl')

# Generate and save 2 synthetic records for now (for testing)
print(f"Saving data to {filename}")

with open(filename, 'w', encoding='utf-8') as f:
    for i in range(50):
        print(f"Generating record {i + 1}/50...")
        data = safe_generate_interview_data()
        f.write(json.dumps(data) + "\n")

print(f"Synthetic interview data saved to: {filename}")
