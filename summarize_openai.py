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
            {"role": "system", "content": "You are a helpful assistant. Your job is to summarize the text given by the user. Answer in the user's language as concisely as possible. Write extensively so that all of the points come through. In the end, present the most important topics of the user's text and their main points. Use at least two sentences for each main point. Tell the user what they should learn from the text."},
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

def main():
    file = open("Transcriptions/transcription_2024-09-12_18-32-53.txt", "r")
    content = file.read()
    file.close()
    summarized_text = summarize_text(content)
    print(summarized_text)

if __name__ == "__main__":
    main()