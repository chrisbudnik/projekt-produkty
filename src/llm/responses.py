from openai import OpenAI


def get_llm_response(prompt: str, model: str = "gpt-4.1") -> str:
    """
    Get a response from the OpenAI LLM.

    Args:
        prompt (str): The input prompt for the LLM.
        model (str): The model to use for generating the response.

    Returns:
        str: The response from the LLM.
    """
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip() if response.choices else ""