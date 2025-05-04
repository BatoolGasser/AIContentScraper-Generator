from langchain_groq import ChatGroq

# Load configuration from environment variables or secrets
GROQ_API_KEY = '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'
MODEL_NAME = "Gemma2-9b-It"
REQUEST_TIMEOUT = 10
MAX_CONTENT_LENGTH = 30000  # Maximum content length to avoid token overflow

# Initialize LLM
model = ChatGroq(
    groq_api_key=GROQ_API_KEY, 
    model=MODEL_NAME, 
    temperature=0.7
)