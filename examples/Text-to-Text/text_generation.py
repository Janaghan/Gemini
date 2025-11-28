# ---------- Imports ----------
from log_setup import log
from google.genai import types, Client
from config import client   



# ---------- Updated Function ----------
def generate_text(prompt):
    # Log request
    log("request", {"prompt": prompt})


    # Generate text
    response_text = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    response_text = response_text.text
    # Log response
    log("response", {"response": response_text})

    return response_text



if __name__ == "__main__":
    print(generate_text("Tell me places to visit in Chennai."))
