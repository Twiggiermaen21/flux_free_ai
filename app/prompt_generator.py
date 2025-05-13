import os
from together import Together
import streamlit as st

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


def get_detailed_prompt_from_model(client, base_prompt: str, model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", max_tokens: int = 1000, temperature: float = 1, stream: bool = True):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Respond clearly and concisely."},
        {"role": "user", "content": generate_detailed_prompt(base_prompt)}
    ]
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
            content = token.choices[0].delta.content if hasattr(token.choices[0].delta, "content") else ""
            if content:
                detailed_prompt += content
                detailed_prompt_container.write(detailed_prompt)
        return detailed_prompt.strip()
    except Exception as e:
        print(f"Error generating prompt: {e}")
        return ""