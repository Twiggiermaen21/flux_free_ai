import os
import base64
from together import Together
from dotenv import load_dotenv

load_dotenv()

def generate_detailed_prompt(baseprompt):
    detailed_prompt = (
        f"Expand on the concept: {baseprompt}. "
        "Create a highly detailed description for a text-to-image AI model, incorporating the following elements: "
        "1. A vivid and intricate description of the main subject of the image, including specific features, expressions, or actions. "
        "2. A well-defined setting or background that complements the main subject, specifying the environment, time of day, and any specific weather or lighting conditions. "
        "3. The mood or atmosphere conveyed by the scene, using descriptive language to evoke emotions or ambiance. "
        "4. Specific colors, artistic styles, or visual aesthetics that should be emphasized to align with the intended theme or mood. "
        "5. Any additional elements or secondary subjects that should be included to enhance the narrative or visual complexity of the image."
    )
    return detailed_prompt

def create_client():
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY nie został ustawiony.")
    return Together(api_key=api_key)

def create_message(role: str, content: str) -> dict:
    return {"role": role, "content": content}

def generate_messages(base_prompt: str) -> list:
    system_message = create_message("system", "You are a helpful assistant. Respond clearly and concisely.")
    user_message = create_message("user", generate_detailed_prompt(base_prompt))
    return [system_message, user_message]


def get_detailed_prompt_from_model(client, base_prompt: str, model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", 
                 max_tokens: int = 100, temperature: float = 1, stream: bool = True):
    messages = generate_messages(base_prompt)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        max_tokens=max_tokens,
        temperature=temperature
    )

    detailed_prompt = ""
    for token in response:
        if hasattr(token, 'choices'):
            detailed_prompt += token.choices[0].delta.content

    return detailed_prompt.strip()

def generate_image(client, prompt):
    response = client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell-Free",
        width=1440,
        height=1440,
        steps=4,
        n=1,
        response_format="b64_json",
    )

    if not response.data:
        raise ValueError("Nie otrzymano danych obrazu.")

    image_data = response.data[0].b64_json
    image_bytes = base64.b64decode(image_data)

    folder = 'images'
    os.makedirs(folder, exist_ok=True)

    index = 1
    while os.path.exists(os.path.join(folder, f"generated_image_{index}.png")):
        index += 1

    output_path = os.path.join(folder, f"generated_image_{index}.png")

    with open(output_path, "wb") as file:
        file.write(image_bytes)

    print(f"Obraz zapisano jako {output_path}")
    return output_path

def main():
    try:
        client = create_client()

        baseprompt = "A futuristic cityscape at sunset"
        print(f"Generowanie szczegółowego promptu dla: {baseprompt}")

        detailed_prompt = get_detailed_prompt_from_model(client, baseprompt)
        print(f"Rozwinięty prompt:\n{detailed_prompt}\n")

        output_path = generate_image(client, detailed_prompt)
        print(f"Obraz wygenerowano i zapisano w: {output_path}")

    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    main()
