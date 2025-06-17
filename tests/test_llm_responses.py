from unittest.mock import MagicMock, ANY
from llm.responses import get_llm_response


def test_get_llm_response_structured_mock(): 
    fake_choice = MagicMock()
    fake_choice.message.content = "it's a test"

    mock_response = MagicMock()
    mock_response.choices = [fake_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    prompt = "Say 'it's a test'"
    result = get_llm_response(mock_client, prompt)

    assert result == "it's a test"
