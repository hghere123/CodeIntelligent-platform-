from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI()


class AssistantService:
    """Simple AI assistant service."""

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    async def complete(self, prompt: str) -> str:
        response = client.responses.create(model=self.model, input=prompt)
        return response.output_text


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
async def chat(prompt: str) -> dict[str, str]:
    service = AssistantService()
    return {"message": await service.complete(prompt)}


def unused_helper() -> str:
    return "unused"

