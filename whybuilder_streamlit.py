from openai import OpenAI
import streamlit as st
import send_and_retrieve
from api_info import API_KEY, whybuilder_assistant_id
from firebase_related import checkSignIn, getThreadId, signUp, saveChat

client = OpenAI(api_key=API_KEY)

with st.sidebar:
    openai_api_key = API_KEY
    #openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password", value=my_api_key)
    #실제로 서비스 할떄는 인풋받지 말고 변수에 그냥 할당 해놓고 사용, value = 라는 변수 추가시 미리 써있는 디폴트값 설정 가능

    st.title('로그인')
    #st.text("🍊서비스 사용을 위해 닉네임을 입력해주세요.")
    #input_user_id = st.text_input('[닉네임 입력]') 
    input_user_id = st.text_input('닉네임으로 로그인') 

    st.caption('닉네임을 입력하고 대화를 시작해요   \n👆 와이빌더가 처음이신가요? 등록이 필요해요')#버튼 + 로그인 성공으로 바꾸기, -> 닉네임 잘못  입력시에도 알림 뜨는걸로 수정
    login_btn = st.button("로그인")
    if login_btn:
        if checkSignIn(inputUsername = input_user_id):
            st.info("로그인 되었습니다. 서비스 사용을 시작해주세요!")
        else : 
            st.info("닉네임이 틀렸습니다.") #닉네임이 틀렸거나 대화이용횟수를 초과하였습니다.
    input_thread_id = getThreadId(id = input_user_id)

        


    st.write("<br><br>", unsafe_allow_html=True) #빈칸 여백

    st.title('닉네임 등록')
    new_user_id = st.text_input('✅ 새로운 닉네임 등록') 
    st.caption('닉네임을 기억하지 못하면 대화 저장이 어려워요    \n등록하신 닉네임은 꼭 기억해주세요') 
    signup_btn = st.button("닉네임 등록") 
    if signup_btn:
        if checkSignIn(new_user_id):
            st.info("이미 존재하는 닉네임입니다.") 
        else:
            signUp(new_user_id)
            st.info("성공적으로 닉네임이 등록되었습니다!") 


st.title("💬 WhyBuilder")
#st.caption("🚀 와이빌더를 통해 목표에 대한 여러분의 열정과 동기를 명확히 하고, 그 목표 달성을 위한 실질적인 첫걸음을 내딛으세요.")
st.caption("🚀 와이빌더와 대화하고 목표를 구체화해요 \n목표를 향한 열정과 동기를 와이빌더에 저장해요.")

image_paths = ["assets/bright_woman_moti.webp", "assets/man_moti.webp", "assets/red_woman_moti.webp"]
# 두 이미지를 나란히 표시, 만약 한개면 경로를 리스트 자리에 바로 넣기
st.image(image_paths, width=100)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "좌측 메뉴바에 닉네임을 입력하고 '와이빌더'에게 인사를 건네주세요!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_prompt := st.chat_input(): #변수를 할당받는 동시에, 할당받는 여부에 대한 bool을 return
    if not input_user_id or input_thread_id is None:  # 로그인 여부를 확인
        st.info("왼쪽 메뉴바를 열고, 로그인 후 '와이빌더'에게 인사를 건네주세요")
        st.stop() 

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    saveChat(
        username = input_user_id,
        role = 'user',
        prompt = user_prompt
        )
    st.chat_message("user").write(user_prompt)

    send_and_retrieve.sendMessagetoThread(thread_id = input_thread_id,
                                           user_prompt = user_prompt,
                                           )
    answer_prompt = send_and_retrieve.runAndRetrieveData(
        assistant_id = whybuilder_assistant_id,
        thread_id = input_thread_id,
        )

    st.session_state.messages.append({"role": "assistant", "content": answer_prompt})
    saveChat(
        username = input_user_id,
        role = 'assistant',
        prompt = answer_prompt
        )
    st.chat_message("assistant").write(answer_prompt)
