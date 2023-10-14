import openai
from config import *

openai.api_key = openai_token

import asyncio

async def rewrite(text, prompt):
    try:
        content = '%s\n%s' %(text, prompt)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": content}
            ])
        print(completion.choices[0].message.content)
        return completion.choices[0].message.content
    except Exception as e:
        print(e)
        return None
    
asyncio.run(rewrite('Сформулируй 3 идеи для бизнеса', 'пожалуйста'))