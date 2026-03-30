"""
Gemini Generator for Malayalam RAG - Updated for gemini-2.5-flash
"""
import google.generativeai as genai
import os
import time
from typing import List

class GeminiGenerator:
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini API with rate limit handling
        
        Args:
            api_key: Your Gemini API key
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use the working model
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(self.model_name)
    
    def generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """
        Generate Malayalam answer using Gemini API with rate limit handling
        """
        # Combine context chunks
        context = "\n\n".join(context_chunks[:3])  # Use top 3 chunks
        
        # Create Malayalam-specific prompt
        malayalam_prompt = f"""ഈ വിവരങ്ങൾ ഉപയോഗിച്ച് മാത്രം ചോദ്യത്തിന് ഉത്തരം നൽകുക.

വിവരങ്ങൾ:
{context}

ചോദ്യം: {question}

നിർദ്ദേശങ്ങൾ:
1. വിവരങ്ങളിൽ നിന്ന് നേരിട്ട് ഉത്തരം നൽകുക
2. വിവരങ്ങൾ പര്യാപ്തമല്ലെങ്കിൽ, "ഈ വിവരങ്ങളിൽ ഉത്തരം ഇല്ല" എന്ന് പറയുക
3. ഉത്തരം മലയാളത്തിൽ മാത്രം നൽകുക

ഉത്തരം (മലയാളത്തിൽ):"""
        
        # CRITICAL: Add delay to avoid rate limits (15 requests/minute)
        time.sleep(4)  # 4 seconds between calls = 15 calls/minute
        
        # Generate response with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    malayalam_prompt,
                    generation_config={
                        "temperature": 0.2,
                        "max_output_tokens": 1000,
                    }
                )
                
                if response.text:
                    return response.text.strip()
                else:
                    return "ഉത്തരം ലഭ്യമാക്കാനായില്ല."
                    
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a rate limit error (429)
                if "429" in error_msg or "quota" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10  # Wait 10, 20 seconds
                        print(f"⏳ Rate limit hit. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "API ക്വോട്ട പൂർത്തിയായി. കുറച്ച് നിമിഷങ്ങൾക്ക് ശേഷം വീണ്ടും ശ്രമിക്കുക."
                else:
                    return f"Gemini API പിശക്: {error_msg[:100]}"
        
        return "പിശക് സംഭവിച്ചു. വീണ്ടും ശ്രമിക്കുക."

# Quick test
if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("Testing Gemini 2.5 Flash with Malayalam...")
        generator = GeminiGenerator(api_key)
        
        # Test with simple context
        test_context = [
            "മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്.",
            "കേരളത്തിന്റെ തലസ്ഥാനം തിരുവനന്തപുരമാണ്."
        ]
        
        test_question = "കേരളത്തിന്റെ തലസ്ഥാനം എന്താണ്?"
        
        answer = generator.generate_answer(test_question, test_context)
        print(f"Q: {test_question}")
        print(f"A: {answer}")
    else:
        print("GEMINI_API_KEY not set in environment")