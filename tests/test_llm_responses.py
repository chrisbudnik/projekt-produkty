from unittest.mock import MagicMock
from src.llm.responses import get_llm_response


def test_get_llm_response():

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="its a test"))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    prompt = "Say 'its a test'"
    result = get_llm_response(mock_client, prompt)

    assert result == "test"
