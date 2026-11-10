import streamlit as st
from config import client, MODEL_NAME, HEALTH_INSTRUCTIONS

st.title("💬 Health Assistant")

st.write(
    "Ask questions about general health, wellness, "
    "symptoms, nutrition, and medicines."
)

st.warning(
    "This assistant provides general health information, "
    "not a medical diagnosis."
)

# Initialise session state
if "health_messages" not in st.session_state:
    st.session_state.health_messages = []

if "health_chats" not in st.session_state:
    st.session_state.health_chats = []

if "health_chat_id" not in st.session_state:
    st.session_state.health_chat_id = 0

with st.sidebar:
    st.subheader("Assistant Settings")

    model = st.selectbox(
        "Model",
        [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b"
        ],
        key="assistant_model"
    )

    if st.button("➕ New Conversation"):
        if st.session_state.health_messages:
            st.session_state.health_chats.insert(
                0,
                {
                    "title": next(
                        (
                            m["content"][:35]
                            for m in st.session_state.health_messages
                            if m["role"] == "user"
                        ),
                        "Health conversation"
                    ),
                    "messages": st.session_state.health_messages.copy()
                }
            )

        st.session_state.health_messages = []
        st.session_state.health_chat_id += 1
        st.rerun()

    st.subheader("Recent Conversations")

    for index, chat in enumerate(st.session_state.health_chats):
        if st.button(chat["title"], key=f"health_chat_{index}"):
            st.session_state.health_messages = chat["messages"].copy()
            st.rerun()

# Display current conversation
for message in st.session_state.health_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a health question...")

if prompt:
    st.session_state.health_messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.responses.create(
                    model=model,
                    instructions=HEALTH_INSTRUCTIONS,
                    input=st.session_state.health_messages
                )

                answer = response.output_text

                if not answer:
                    answer = "I could not generate a response. Please try again."

                st.markdown(answer)

                st.session_state.health_messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as error:
                st.session_state.health_messages.pop()

                st.error("The request failed. Check the model and API limits.")
                st.caption(str(error))