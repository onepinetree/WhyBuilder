from openai import OpenAI
from api_info import API_KEY

client = OpenAI(api_key = API_KEY)

def createThread()->str:
    '''Thread를 생성하고 thread의 id를 return 하는 함수'''
    empty_thread = client.beta.threads.create()
    return empty_thread.id

def deleteThread(thread_id: str):
    response = client.beta.threads.delete(thread_id)
    print(response)

#thread_messages = (client.beta.threads.messages.list(my_thread_id)).data[0].content[0].text.value
#print(thread_messages), 이것으로 thread정보접근 가능

def extractPromptfromThread(thread_id : str)->dict:
    '''thread_id를 입력하면 현재 상태의 대화의 축적을 role:value의 dict의 형태로 return해주는 함수'''
    '''{'assistant_0': 'gpt_prompt', 'user_0': 'user_prompt'}'''
    prompt_data = {}
    thread = client.beta.threads.messages.list(thread_id)
    thread_data_list = thread.data
    i = 0
    for thread_message in thread_data_list:
        if len(thread_message.content) > 0:
            prompt_data[f'{thread_message.role}_{i}'] = thread_message.content[0].text.value
            print(f'{thread_message.role}_{i} : {thread_message.content[0].text.value}')
            i += 1

    return prompt_data

