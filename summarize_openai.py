from openai import OpenAI
from envero import environment_variables
import os

def summarize_text(text, model="gpt-4o-mini", write_output=False, output_directory="./Summarizations", filename="summarization"):
    env_vars = environment_variables()

    client = OpenAI(api_key=env_vars["OPENAI_API_KEY"],
                    organization=env_vars["OPENAI_ORG_ID"]) 

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Your job is to summarize the text given by the user. Answer in the user's language as concisely as possible."},
            {
                "role": "user",
                "content": text
            }
        ]
    )

    # Get model response
    summarized_text = completion.choices[0].message.content.encode("utf-8").decode()

    # Save summarization
    if write_output:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_file = output_directory + "/" + filename + ".txt"
        with open(output_file, "w", encoding="utf-8") as txt:
            txt.write(summarized_text)
        print(f"Summariation saved to {output_file}")

    return summarized_text
