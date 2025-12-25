from openai import OpenAI
try:
    client = OpenAI(api_key="fake")
    print(f"Has responses: {hasattr(client, 'responses')}")
    print(f"Has chat: {hasattr(client, 'chat')}")
except Exception as e:
    print(e)
