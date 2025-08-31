import streamlit as st
import requests

if "resume" not in st.session_state:
    st.session_state.resume = None

st.title("Résumé et conversation sur un document")
st.header("genration de doc à patir d'un doc txt ")
upload_file = st.file_uploader("upload un fichier", type=["txt"])

if upload_file is not None:
    files = {"fich": (upload_file.name, upload_file.read(), upload_file.type)}
    if st.button("résume"):
        response = requests.post("http://127.0.0.1:8000/initialize", files=files)
        if response.status_code == 200:
            st.session_state.resume = response.json().get("summarize")
        else:
            st.write("erreur de chargement")

1
if st.session_state.resume:
    st.write("résumé : ")
    st.write(st.session_state.resume)


st.header("chatbot")
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("commencer une conversation")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    response = requests.post(
        "http://127.0.0.1:8000/update",
        data={"request": user_input},
        stream=True,
    )
    if response.status_code == 200:
        print(response)
        response_text = ""
        for chunk in response.iter_lines():
            if chunk:
                response_text += chunk.decode("utf-8")
        st.session_state.history.append({"role": "bot", "content": response_text})
    else:
        st.write("erreur")

for message in st.session_state.history:
    if message["role"] == "user":
        st.write("    ", message["content"])
    else:
        st.write("bot : ", message["content"])
