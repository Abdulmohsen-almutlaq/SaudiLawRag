from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def generate_response(prompt_text):
    # Model ID from Hugging Face
    model_id = "humain-ai/ALLaM-7B-Instruct-preview"

    print(f"Loading {model_id}...")
    
    # Load the tokenizer and model
    # Note: Requires a GPU for 7B models. torch_dtype=torch.float16 reduces memory usage.
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    # Format the messages. Since this is an Instruct model, we should use a chat template if available,
    # or structure it specifically based on ALLaM's recommended prompt template.
    messages = [
        {"role": "user", "content": prompt_text}
    ]

    try:
        # Try using the chat template
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    except Exception:
        # Fallback if no chat template is defined
        prompt = f"User: {prompt_text}\nAssistant:"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    print("Generating response...")
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

    # Extract only the newly generated text, skipping the input prompt
    input_length = inputs.input_ids.shape[1]
    generated_tokens = outputs[0][input_length:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    return response

if __name__ == "__main__":
    sample_question = "ما هي حقوق العامل في فترة التجربة حسب نظام العمل السعودي؟"
    answer = generate_response(sample_question)
    print("\nالإجابة:\n")
    print(answer)
