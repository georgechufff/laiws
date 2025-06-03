import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import torch
from text_extractor import TextExtractor 
import os
import warnings
from prompts import TRANSLATION_PROMPT, INTRODUCTION_PROMPT
from configs import sync_openai_api

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

st.set_page_config(page_title='LWAIS', page_icon='🐍', initial_sidebar_state='collapsed')
st.title("LWAIS")

try:
    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-large"
    )
    vector_store = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )

except Exception as e:
    warnings.warn("FAISS Database seems to not exist. Trying to recover it manually.")
    from db_creating import vector_store

def page_1():
    placeholder.empty()
    st.session_state['current_state'] = 1

def page_2():
    placeholder.empty()
    st.session_state['current_state'] = 2

def page_3():
    placeholder.empty()
    st.session_state['current_state'] = 3

placeholder = st.empty()

if 'current_state' not in st.session_state:
    st.session_state['current_state'] = 1

if st.session_state['current_state'] == 1:

    with st.form(key='signin', clear_on_submit=True):
        st.subheader('Войти в аккаунт')
        username = st.text_input('Имя пользователя', placeholder='Введите имя пользователя')
        password = st.text_input('Пароль', placeholder='Введите пароль') 

        _, btn1, btn2, _ = st.columns(4)
        with btn1:
            st.form_submit_button('Войти', on_click=page_3)

        with btn2:
            st.form_submit_button('Регистрация', on_click=page_2)

elif st.session_state['current_state'] == 2:

    with st.form(key='signup', clear_on_submit=True):
        st.subheader('Зарегистрироваться в системе')
        email = st.text_input('Электронная почта', placeholder='Введите почту')
        username = st.text_input('Имя пользователя', placeholder='Введите имя пользователя')
        password1 = st.text_input('Пароль', placeholder='Введите пароль') 
        password2 = st.text_input('Пароль', placeholder='Введите пароль еще раз')

        if email:
            if validate_email(email):
                if username and len(username) >= 2:
                    if len(password1) >= 6 and password1 == password2:
                        print(username)
                    else:
                        st.warning('Проблема с паролем. Убедитесь в том, что пароли совпадают.')
                else:
                    st.warning('Имя пользователя не введено или слишком короткое')
            else:
                st.warning('Недопустимая электронная почта.')


        _, btn3, btn4, _ = st.columns(4)
        with btn3:
            st.form_submit_button('Войти в аккаунт', on_click=page_1)
        with btn4:
            st.form_submit_button('Регистрация', on_click=page_3)

elif st.session_state['current_state'] == 3:

    uploaded_file = st.file_uploader(
        'Приложите файл',
        accept_multiple_files=False,
    )

    if uploaded_file:
        
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        text = TextExtractor(uploaded_file.name)
        file_content = text.load()
        print(file_content)
        os.remove(uploaded_file.name)
    
    else:
        file_content = None

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": INTRODUCTION_PROMPT}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Введите Ваше сообщение.")

    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})            

        with st.chat_message("assistant"):

            query = st.session_state.messages[-1]['content']
            
            if file_content:
                query += ('\n' + file_content) 

            content = vector_store.similarity_search(query, k=4)
            docs_content = "\n\n".join(doc.metadata['source'] + ': \n' + doc.page_content for doc in content)
            
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": TRANSLATION_PROMPT
                        },
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query,
                        },
                    ]
                },
            ]

            answer = sync_openai_api(messages)
            response = st.write_stream([s + ' ' for s in answer.split()])
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
