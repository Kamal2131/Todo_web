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
                    "content": f"""Convert natural language TODO inputs to JSON with these STRICT rules:

                1. Structure:
                {{
                    "task": "Concise title (5-7 words max)",
                    "description": "Extracted details from input (MUST include even if brief)",
                    "category": ["work", "personal", "shopping", "other"],
                    "priority": ["low", "medium", "high"],
                    "due_date": "YYYY-MM-DD | null"
                }}

                2. Examples:
                Input: "Finish report by Friday"
                Output: {{
                    "task": "Finish report",
                    "description": "Complete and submit weekly report",
                    "category": "work",
                    "priority": "medium",
                    "due_date": "{ (date.today() + timedelta(days=(4 - date.today().weekday()) % 7)).isoformat() }"
                }}

                Input: "Buy milk"
                Output: {{
                    "task": "Buy milk",
                    "description": "Purchase 2 liters of whole milk",
                    "category": "shopping",
                    "priority": "medium",
                    "due_date": null
                }}

                3. Requirements:
                - Current Date: {date.today().isoformat()}
                - ALWAYS include description (extract key details from input)
                - Convert relative dates ("tomorrow" = +1 day)
                - No markdown, ONLY valid JSON
                - For minimal inputs, expand description logically"""
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