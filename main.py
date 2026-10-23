import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load the variables from the .env file
load_dotenv()

# 2. Retrieve your specific key
gemini_key = os.getenv("gemini_api_key")

if not gemini_key:
    raise ValueError("API key not found. Check your .env file.")

# Use a model string directly from your diagnostic list
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash", 
    google_api_key=gemini_key,
    temperature=0 
)

# 4. Invoke the model
user_message = "What are the core components of an enterprise ASP.NET backend?"
response = llm.invoke(user_message)

print(response.content)