import os
import streamlit as st
from dotenv import load_dotenv
from prompt_generator import get_detailed_prompt_from_model
from image_generator import generate_image
from upscaling import upscale_image
from together import Together

load_dotenv()

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
    "2:1 - 1440x720": (1440, 720),
    "5:4 - 1280x1024": (1280, 1024),
}
steps = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
}

selected_resolution = st.selectbox("Select Resolution:", list(resolutions.keys()))
selected_steps = st.selectbox("Select steps:", list(steps.keys()))

width, height = resolutions[selected_resolution]

base_prompt = st.session_state["base_prompt"]
generate_button = st.button("Generate Image")

if generate_button:
    with st.spinner("Generating image..."):
        try:
            api_key = os.getenv("TOGETHER_API_KEY")
            client = Together(api_key=api_key)

            detailed_prompt = get_detailed_prompt_from_model(client, base_prompt)
            if detailed_prompt:
                image_path = generate_image(client, detailed_prompt, width, height,selected_steps)
        except Exception as e:
            st.error(f"Error: {e}")

        if image_path:
            st.image(image_path)
            st.success(f"Image generated successfully and saved as {image_path}")
            upscale_image(image_path, "upscaled_" + image_path)
            st.success("Image upscaled to 300 DPI and saved.")
        else:
            st.error("Failed to generate image.")
