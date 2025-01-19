import google.generativeai as genai
import yaml
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, config_filepath="config.yaml"):
        self.config = self.load_config(config_filepath)
        self.api_key = self.config['gemini']['api_key']
        if not self.api_key:
            raise ValueError("Missing api_key in config file.")

        genai.configure(api_key=self.api_key)

        # --- Updated model and system instruction ---
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction="""
            You are a helpful and informative career advisor for high school students. 
            Your name is **Pathfinder**.
            Your role is to guide students in exploring career paths, understanding educational requirements, and making informed decisions about their future.
            Provide answers that are:
            1. Clear and easy to understand, avoiding technical jargon.
            2. Concise and to the point, without unnecessary elaboration.
            3. Keep answers relatively short, ideally under 5-6 sentences, unless more detail is absolutely necessary.
            4. Always stay within the context of career counseling for high school students. If a question is outside this scope, politely steer the conversation back to career-related topics.
            """
        )
        # --------------------------------------------

        self.chat_histories = {}

    def load_config(self, filepath):
        """Loads configuration from a YAML file."""
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def generate_response(self, chat_id: str, prompt: str) -> str:
        """
        Generates a response using Gemini, maintaining conversation context in memory.
        """
        try:
            # Get chat history (or initialize if it doesn't exist)
            if chat_id not in self.chat_histories:
                self.chat_histories[chat_id] = []
                # AI starts the conversation with an introductory message
                intro_message = "Hi there! I'm Pathfinder, your career advisor. I'm here to help you explore career options, understand your interests, and plan your future. What's on your mind today?"
                self.chat_histories[chat_id].append({"role": "model", "parts": [intro_message]})

            history = self.chat_histories[chat_id]

            # Add user prompt to history
            history.append({"role": "user", "parts": [prompt]})

            # Use the chat interface to generate content
            chat = self.model.start_chat(history=history)
            response = chat.send_message(prompt)

            # Parse the response before adding to history and returning
            parsed_response = self.parse_response(response.text)

            # Add model's response to history
            history.append({"role": "model", "parts": [parsed_response]})

            # Update chat history
            self.chat_histories[chat_id] = history

            logger.info(f"Chat ID: {chat_id} - User prompt: {prompt}")
            logger.info(f"Generated response: {parsed_response}")  # Log the parsed response
            return parsed_response  # Return the parsed response
        except Exception as e:
            logger.exception(f"Error in generate_response: {e}")
            raise

    def parse_response(self, text: str) -> str:
        """
        Parses and cleans the response text to remove unwanted formatting and normalize spacing.
        
        Args:
            text (str): Raw text response from Gemini API
            
        Returns:
            str: Cleaned and formatted text
        """
        # Remove quotes at the start and end of the text if they exist
        text = text.strip('"')
        
        # Replace various newline representations
        text = text.replace('\\n', '\n')  # Replace literal \n with newline
        text = text.replace('|n', '\n')   # Replace |n with newline
        text = text.replace('\\\\n', '\n') # Replace escaped \n with newline
        
        # Handle bullet points
        text = text.replace('\\n- ', '\n• ') # Replace newline dash with bullet
        text = text.replace('\n- ', '\n• ')  # Replace newline dash with bullet
        text = text.replace('In- ', '\n• ')  # Replace "In-" with newline bullet
        
        # Clean up other special formatting
        text = text.replace('nlf', '')    # Remove nlf
        text = text.replace('In', '\n')   # Replace "In" with newline
        
        # Remove excessive quotes
        text = text.replace('""', '"')    # Replace double quotes with single quotes
        
        # Fix spacing issues
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove extra spaces
            line = ' '.join(line.split())
            cleaned_lines.append(line)
        
        # Join lines with proper spacing
        text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        # Clean up any remaining formatting artifacts
        text = text.replace('\\t', '    ')  # Replace tabs with spaces
        text = text.replace('\\"', '"')     # Fix escaped quotes
        text = text.replace('\\\'', "'")    # Fix escaped single quotes
        
        return text.strip()