import google.generativeai as genai

genai.configure(api_key="AIzaSyBkpokM016r_-fzMHRZusEGLry_c8Npt-o") 

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Say hello in one sentence.")
print(response.text)