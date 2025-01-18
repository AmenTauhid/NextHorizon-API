import google.generativeai as genai
import yaml

def load_config(filepath="config.yaml"):
    """Loads configuration from a YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

# Load the configuration
config = load_config()
api_key = config['gemini']['api_key']

# Configure the Gemini API
genai.configure(api_key=api_key)

# Choose your Gemini model
model = genai.GenerativeModel('gemini-pro')

def generate_text(prompt: str) -> str:
    """
    Generates text using Gemini based on the provided prompt.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in gemini_service: {e}")
        raise