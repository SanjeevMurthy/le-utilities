from openai import OpenAI

endpoint = "https://try-custom-llm.services.ai.azure.com/openai/v1/"
model_name = "Phi-4"
deployment_name = "Phi-4"

api_key = "GAd1coD5FPSBX3W5sTm5WIeqVG8tfy5UGO3HEoGHQSDomOmrjtR7JQQJ99BLACYeBjFXJ3w3AAAAACOG6Byr1234"

client = OpenAI(
    base_url=f"{endpoint}",
    api_key=api_key
)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of Karnataka?",
        }
    ],
)

print(completion.choices[0].message)

#print api response as json 
print(completion.choices[0])