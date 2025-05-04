import os
import json
from datetime import date, timedelta
from groq import Groq
from dotenv import load_dotenv
from ..schemas import TodoCreate

load_dotenv()

class GroqProcessingError(Exception):
    """Custom exception for Groq processing failures"""

def parse_todo(natural_text: str) -> TodoCreate:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    today = date.today().isoformat()
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{
                    "role": "system",
                    "content": f"""Convert natural language TODO inputs to JSON with these rules:

                1. Structure:
                {{
                    "task": "Concise title (5-7 words max)",
                    "description": "Key details from input | null",
                    "category": ["work", "personal", "shopping", "other"],
                    "priority": ["low", "medium", "high"],
                    "due_date": "YYYY-MM-DD | null"
                }}

                2. Examples:
                Input: "Finish report by Friday with client feedback"
                Output: {{
                    "task": "Finish client report",
                    "description": "Include client feedback",
                    "category": "work",
                    "priority": "high",
                    "due_date": "{ (date.today() + timedelta(days=(4 - date.today().weekday()) % 7)).isoformat() }"  # Next Friday
                }}

                Input: "Buy milk and eggs"
                Output: {{
                    "task": "Buy groceries",
                    "description": "Milk and eggs",
                    "category": "shopping",
                    "priority": "medium",
                    "due_date": null
                }}

                3. Current Date: {date.today().isoformat()}
                4. Handle relative dates ("tomorrow" = +1 day, "next week" = +7 days)
                5. Omit unspecified fields as null
                6. Return ONLY valid JSON"""
                }, {
                    "role": "user",
                    "content": f"Input: {natural_text}\nOutput:"
                }],
            response_format={"type": "json_object"},
            temperature=0.5
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        # Validate required fields
        if not all(key in result for key in ['task', 'category', 'priority']):
            raise ValueError("Missing required fields")

        # Date validation
        if result.get('due_date'):
            try:
                parsed_date = date.fromisoformat(result['due_date'])
                if parsed_date < date.today():
                    raise GroqProcessingError("Due date cannot be in the past")
                result['due_date'] = parsed_date.isoformat()
            except ValueError:
                raise GroqProcessingError(f"Invalid date format: {result['due_date']}")

        return TodoCreate(**result)
        
    except json.JSONDecodeError as e:
        raise GroqProcessingError(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise GroqProcessingError(f"API Error: {str(e)}")