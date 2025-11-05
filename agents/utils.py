from langchain.chat_models import init_chat_model
from const import GOOGLE_API_KEY

model = init_chat_model("google_genai:gemini-2.0-flash-lite")
