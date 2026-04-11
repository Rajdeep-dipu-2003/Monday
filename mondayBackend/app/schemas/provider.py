from pydantic import BaseModel
from enum import Enum

class Provider(str, Enum):
    ollama: "Ollama"
    openai: "OpenAi"
    gemini: "Gemini"