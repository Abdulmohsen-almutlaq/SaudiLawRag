import ollama

def generate_response_ollama(prompt_text, model_name="allam-7b"):
    """
    Calls the ALLaM-7B model hosted locally via Ollama.
    """
    print(f"Sending request to Ollama (model: {model_name})...")
    
    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': prompt_text,
                }
            ]
        )
        return response['message']['content']
    
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}\nMake sure the Ollama service is running and the model '{model_name}' is installed."

if __name__ == "__main__":
    sample_question = "ما هي حقوق العامل في فترة التجربة حسب نظام العمل السعودي؟"
    answer = generate_response_ollama(sample_question)
    
    print("\nالإجابة:\n")
    print(answer)
