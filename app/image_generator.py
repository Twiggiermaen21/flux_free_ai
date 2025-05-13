import os
import base64


def generate_image(client, prompt, width, height,steps):
    response = client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell-Free",
        width=width,
        height=height,
        steps=steps,
        n=1,
        response_format="b64_json",
    )

    if not response.data:
        raise ValueError("No image data received.")

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

    print(f"Image saved as {output_path}")
    return output_path
