from pydantic import BaseModel
from enum import Enum

class Provider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"