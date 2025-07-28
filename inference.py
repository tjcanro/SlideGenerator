import requests

INVOKE_URL = "https://api.brev.dev/v1/chat/completions"
API_KEY = "brev_api_-30Tr0kdRzKy3RTr4k9AtChl7TrL"


def run_inference(prompt: str) -> str:
    """
    Sends `prompt` to the LLM endpoint and returns
    exactly the assistant's message content.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "model": "nvcf:nvidia/llama-3.1-nemotron-nano-8b-v1:dep-30TtAqxOULNBaELk6LSoLPKzNfV",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.5,
        "top_p": 0.7,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }
    resp = requests.post(INVOKE_URL, json=payload, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    # Drill down to the assistant’s reply
    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    prompt = 'Create a slide titled "Agile Principles" with three bullet points, and output it as XML in the following format:\n<slide>\n  <title>…</title>\n  <bullet>…</bullet>\n  <bullet>…</bullet>\n  <bullet>…</bullet>\n</slide>'
    print(run_inference(prompt))
