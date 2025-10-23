import openai

openai.api_key = "sk-xxxxxxxxxxxxxxxx"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a friendly AI health assistant."},
        {"role": "user", "content": "I have fever and headache"}
    ]
)

print(response.choices[0].message.content)
