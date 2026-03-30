import google.generativeai as genai

class FlowchartProcessor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro-vision")

    def image_to_flowchart_text(self, image_base64):
        prompt = """
You are given an educational flowchart image in Malayalam.

TASK:
- Detect whether the image is a flowchart
- If yes, convert it into structured Malayalam text
- Preserve hierarchy and relationships
- Use → to represent flow
- Do NOT add external knowledge
- Output ONLY text

FORMAT:
[FLOWCHART]
Parent → Child
"""

        response = self.model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": image_base64}
        ])

        return response.text.strip()
