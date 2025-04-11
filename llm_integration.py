# llm_integration.py
from openai import OpenAI
from dotenv import load_dotenv
import os
import ast
import re

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def sanitize_name(name: str) -> str:
    """Sanitize LLM-generated names to be valid Python identifiers."""
    name = re.sub(r'\s+', '_', name)  # Replace spaces with underscores
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)  # Remove invalid characters
    if not name or name[0].isdigit():  # Ensure it’s not empty or starting with a digit
        name = '_' + name
    return name

def llm_generate_names(count: int) -> list[str]:
    """Generate a list of plausible variable names using OpenAI's API."""
    prompt = f"Generate {count} plausible variable names for a Python program related to user input handling, one per line, with no additional text or formatting."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates plausible Python variable names."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        names = response.choices[0].message.content.strip().split('\n')
        sanitized_names = [sanitize_name(name) for name in names if sanitize_name(name)]
        return sanitized_names[:count] or [f"var_{i}" for i in range(count)]  # Ensure enough names
    except Exception as e:
        print(f"Error generating names: {e}")
        return [f"var_{i}" for i in range(count)]

def llm_generate_junk_function() -> str:
    """Generate a benign Python function using OpenAI's API."""
    prompt = (
        "Generate a single, complete, and syntactically valid Python function that could be part of a user input validation module. "
        "The function must include at least one comment and take at least one parameter. "
        "Return only the function code with no additional text, markdown, or explanations."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates valid Python functions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        function_code = response.choices[0].message.content.strip()
        # Remove potential markdown or extra text
        function_code = re.sub(r'```(?:python)?\n?|```', '', function_code).strip()
        # Verify the code is valid Python
        ast.parse(function_code)
        return function_code
    except Exception as e:
        print(f"Error generating junk function: {e}")
        print(f"Failed code: {function_code!r}")
        return """
def default_junk_func(data):
    # Fallback function for input validation
    return len(data)
"""