import os
import base64
from together import Together
from dotenv import load_dotenv
import streamlit as st
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

def get_detailed_prompt_from_model( client, base_prompt: str, model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",  max_tokens: int = 100, temperature: float = 1, stream: bool = True):
    messages = generate_messages(base_prompt)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        max_tokens=max_tokens,
        temperature=temperature
    )
    detailed_prompt_container = st.empty()
    detailed_prompt = ""

    try:
        for token in response:
            if hasattr(token, "choices"):
                content = token.choices[0].delta.content if hasattr(token.choices[0].delta, "content") else ""
                if content:
                    detailed_prompt += content
                    detailed_prompt_container.write(detailed_prompt)
        return detailed_prompt.strip()
    except Exception as e:
        print(f"\nBłąd podczas generowania promptu: {e}")
        return ""

def generate_image(client, prompt, width, height):
    response = client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell-Free",
        width=width,
        height=height,
        steps=1,
        n=1,
        response_format="b64_json",
    )

    if not response.data:
        raise ValueError("Nie otrzymano danych obrazu.")

    image_data = response.data[0].b64_json
    image_bytes = base64.b64decode(image_data)

    folder = "images"
    os.makedirs(folder, exist_ok=True)

    index = 1
    while os.path.exists(os.path.join(folder, f"generated_image_{index}.png")):
        index += 1

    output_path = os.path.join(folder, f"generated_image_{index}.png")

    with open(output_path, "wb") as file:
        file.write(image_bytes)

    print(f"Obraz zapisano jako {output_path}")
    return output_path

st.title("Prompt Generator and Image Creator")
st.write("Generate a detailed prompt and an image using the Together API.")
if "base_prompt" not in st.session_state:
    st.session_state["base_prompt"] = "A futuristic city skyline at sunset"

st.session_state["base_prompt"] = st.text_input(
    "Enter a base prompt:", 
    value=st.session_state["base_prompt"], 
    key="base_prompt_key"
)
resolutions = {
    "1:1 - 1440x1440 (Square)": (1440, 1440),
    "3:2 - 1440x960": (1440, 960),
    "16:9 - 1440x810": (1440, 810),
    "2:1 - 1440x720": (1440, 720),
    "5:4 - 1280x1024": (1280, 1024),
}

selected_resolution = st.selectbox("Select Resolution:", list(resolutions.keys()))
width, height = resolutions[selected_resolution]
base_prompt = st.session_state["base_prompt"]
generate_button = st.button("Generate Image")

if generate_button:
    with st.spinner("Generating image..."):
        try:
            client = create_client()  
            detailed_prompt = get_detailed_prompt_from_model(client, base_prompt)
            if detailed_prompt:
                image_path = generate_image(client, detailed_prompt, width, height)
        except Exception as e:
            print(f"Błąd: {e}")

        if image_path:
            st.success(f"Image generated successfully and saved as {image_path}")
            st.image(image_path)
        else:
            st.error("Failed to generate image.")