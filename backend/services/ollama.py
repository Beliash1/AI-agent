import urllib.request
import json

def ask_ollama(prompt: str, model: str = "qwen3:4b"):
    url = "http://127.0.0.1:11434/api/generate"
    
    # მონაცემები, რომლებსაც ვგზავნით
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    # მონაცემების გადაქცევა JSON-ად
    encoded_data = json.dumps(data).encode('utf-8')
    
    # მოთხოვნის შექმნა
    req = urllib.request.Request(url, data=encoded_data, headers={'Content-Type': 'application/json'})
    
    try:
        # მოთხოვნის გაგზავნა
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "")
            
    except Exception as e:
        # თუ ვერ დაუკავშირდა, დააბრუნე შეცდომა
        print(f"DEBUG ERROR: {e}")
        return "შეცდომა: Ollama-სთან დაკავშირება ვერ მოხერხდა. დარწმუნდი რომ 'ollama serve' გაშვებულია."