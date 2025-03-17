from openai import OpenAI
class LLMExtractor:
    def __init__(self):
        self.client = OpenAI()

    def extract_affiliations(self, text: str) -> set:
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": "Write a one-sentence bedtime story about a unicorn."
            }]
        )

        print(completion.choices[0].message.content)
        return None
    

