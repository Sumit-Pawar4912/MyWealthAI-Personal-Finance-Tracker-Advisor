import google.generativeai as genai

genai.configure(api_key='AIzaSyD6hX76Smhvm_8TAweqIpApYnbkKqJ8rKY')

print("Available models:")
for m in genai.list_models():
    print(f"  {m.name}")
