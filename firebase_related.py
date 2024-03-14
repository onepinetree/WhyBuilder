import firebase_admin
from firebase_admin import credentials, firestore
from thread_creator import createThread
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

if not firebase_admin._apps:
    cred = credentials.Certificate('/etc/secrets/whybuilder_database.json')
    app = firebase_admin.initialize_app(cred)

db = firestore.client()
users_ref = db.collection("user")

#docs는 user_collection의 document들, doc.id -> document 자체의 이름
#doc에다가 .to_dict를 적용해 document(map 형태의 정보 한묶음)를 다루기 편한 형태로 만들고 거기서 정보를 가지고 온다.


def checkSignIn(inputUsername: str) -> bool:
    # 효율성을 위해 limit을 사용해서 한개의 문서까지만을 찾음,get은 그냥 부분의 스냡샷을 가지고 오는 용도
    # 'users' 컬렉션에서 'nickname' 필드가 inputUsername와과 일치하는 문서 검색
    # where을 사용해서 계산을 firebase측에서 하도록 해 가져와야하는 정보의 양이 적음
    users_ref = db.collection('user')
    query = users_ref.where('username', '==', inputUsername).limit(1).get()
    return len(query) > 0  # 문서가 존재하면 True, 아니면 False 반환

def getThreadId(id: str) -> str:
    # 'users' 컬렉션에서 'nickname' 필드가 id와 일치하는 문서 검색
    users_ref = db.collection('user')
    query = users_ref.where('username', '==', id).limit(1).get() 
    #query는 iterable(리스트와 비슷)의 형태이므로 반복구조를 사용해야함.
    for doc in query:
        return doc.to_dict().get('thread_id', '')  # 'thread_id' 필드의 값을 반환
    return ''  
    
def signUp(username: str) -> str:
    now = datetime.now()
    if checkSignIn(username) == False:
        doc_ref = db.collection("user").document(username)
        doc_ref.set(
                    {"signup_time": now.strftime("%Y-%m-%d-%H:%M"), 
                     "thread_id": createThread(), 
                     "username": username}
                     )
        return '회원가입이 완료되었습니다'
    return '이미 존재하는 닉네임입니다! 다른 닉네임으로 회원가입을 진행해주세요'
    

def saveChat(username: str, role: str, prompt: str) -> None:
    '''username과 지금 대화의 role과 그의 prompt를 입력하면 시간과 함께 DB에 저장되는 함수'''
    now = datetime.now()
    #계층적 collection/document 접근 방법
    doc_ref = db.collection("user").document(username)
    chat_ref = doc_ref.collection('chat_log').document(now.strftime("%Y-%m-%d"))
    #DocumnetReference객체는 바로 .to_dict() 메소드를 사용할 수 없고 DocumentSnapshot만 가능하다. 그것의 변환과정
    doc_snapshot = chat_ref.get()

    # DocumentSnapshot에서 데이터를 가져온다. 없을 경우 빈 딕셔너리를 사용한다.
    if doc_snapshot.exists:
        updated_chat = doc_snapshot.to_dict()
    else:
        updated_chat = {}

    # 채팅 메시지를 추가한다. 'chat num'을 채팅 메시지의 순번으로 사용한다.
    chat_num = int(updated_chat.get('chat_num', 0))  # 'chat_num'이 없으면 0을 기본값으로 사용
    updated_chat[str(chat_num + 10)] = f'({role}) {prompt}'
    #chat_num을 업데이트한다.
    updated_chat['chat_num'] = chat_num + 1
    # 업데이트된 채팅 데이터로 문서를 설정한다.
    chat_ref.set(updated_chat)

