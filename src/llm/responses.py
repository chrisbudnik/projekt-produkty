from openai import OpenAI


def get_llm_response(client: OpenAI, prompt: str, model: str = "gpt-4.1") -> str:
    """
    Get a response from the OpenAI LLM.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip() if response.choices else ""
