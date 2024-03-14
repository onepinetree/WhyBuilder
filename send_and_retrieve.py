from openai import OpenAI
import time
from api_info import API_KEY

client = OpenAI(api_key = API_KEY)

def sendMessagetoThread(thread_id : str, user_prompt : str):
    '''user의 prompt를 받고 thread에 추가해주는 함수'''
    thread_message = client.beta.threads.messages.create(
    thread_id,
    role="user",
    content=user_prompt,
    )

def runAndRetrieveData(assistant_id : str, thread_id : str) -> str:
    '''thread를 run하고 status를 확인한후 value를 return 해주는 함수'''
    run = client.beta.threads.runs.create(
    thread_id = thread_id,
    assistant_id = assistant_id
    )
    run_id = run.id

    while True:
        retrieve_run = client.beta.threads.runs.retrieve(
        thread_id = thread_id,
        run_id = run_id
        )
        if(retrieve_run.status == 'completed'):
            thread_messages = client.beta.threads.messages.list(thread_id)
            #print(thread_messages.data)
            return thread_messages.data[0].content[0].text.value
            break
        else:
            time.sleep(2)


