import streamlit as st
st.set_page_config(layout="wide")

from backend import research_llm, hc_llm

header_container = st.container()
header_container.title("LLM PoC")
header_container.write("Demonstration on some of the capabilities of Large Language Models (LLM) related to WS")
header_container.image('https://dse-public-data.s3.amazonaws.com/DSE_approved.png', width=300)

rs, hc = st.tabs(["Technical Research","WS Helpcenter"])

if 'research_qna' not in st.session_state:
    st.session_state['research_qna'] = []
if 'hc_qna' not in st.session_state:
    st.session_state['hc_qna'] = []
if 'current_tab' not in st.session_state:
    st.session_state['current_tab'] = 'research_qna'

if st.session_state['current_tab'] == 'research_qna':
    # hi im richie
    # what is my name
    # what is the rsi of netflix as of 2020-09-21?
    # what dates did golden cross occur for Netflix in 2016?
    # if i bought $1000 worth of Netflix at beginning of 2016, how much profit would i have made by the end of the year?
    with rs:
        question_container = st.container()
        result_container = st.container()

        with question_container:
            with st.form("research_form", clear_on_submit=True):
                "bot: Hi, I am Wealthsimple's trusted AI agent! Let me help you with technical market research."
                user_input = st.text_input("type in your questions: ", key='rs_q')
                submitted = st.form_submit_button("Submit")
                if submitted and user_input:
                    st.session_state['research_qna'].append(f"user: {user_input}")
        
        with result_container:
            for i in st.session_state['research_qna']:
                st.text(i)
            if submitted and user_input:
                placeholder = st.empty()
                placeholder.text("bot: typing...")
                try:
                    res = research_llm.run(input=user_input)
                except ValueError as e:
                    res = research_llm.run(input=user_input)
                st.session_state['research_qna'].append(f"bot: {res}\n")
                placeholder.empty()
                st.text(f"bot: {res}\n")

    # explain to me the difference between tfsa and rrsp
    # where do i check how much contribution room i have for tfsa?
    # i want to DRS my shares.
    # what's the fee for foreign transactions on your cash card
    # are my funds safe with wealthsimple?
    # i want to assign my beneficiary for RESP
    # what is wealthsimple invest? how is it different from trade?
    # does wealthsimple support options?
    with hc:
        question_container = st.container()
        result_container = st.container()
        
        with question_container:
            with st.form("hc_form", clear_on_submit=True):
                "bot: Hi, I am Wealthsimple's trusted AI agent! I can answer all WS related questions."
                user_input = st.text_input("type in your questions: ", key='hc_q')
                submitted = st.form_submit_button("Submit")
                if submitted and user_input:
                    st.session_state['hc_qna'].append(f"user: {user_input}")
                st.session_state['current_tab'] = 'hc_qna'

        with result_container:
            for i in st.session_state['hc_qna']:
                st.text(i)
            if submitted and user_input:
                placeholder = st.empty()
                placeholder.text("bot: typing...")
                try:
                    res = hc_llm.run(input=user_input)
                except ValueError as e:
                    res = hc_llm.run(input=user_input)
                st.session_state['hc_qna'].append(f"bot: {res}\n")
                placeholder.empty()
                st.text(f"bot: {res}\n")
else:
    with rs:
        question_container = st.container()
        result_container = st.container()

        with question_container:
            with st.form("research_form", clear_on_submit=True):
                "bot: Hi, I am Wealthsimple's trusted AI agent! Let me help you with technical market research."
                user_input = st.text_input("type in your questions: ", key='rs_q')
                submitted = st.form_submit_button("Submit")
                if submitted and user_input:
                    st.session_state['research_qna'].append(f"user: {user_input}")
                st.session_state['current_tab'] = 'research_qna'
        
        with result_container:
            for i in st.session_state['research_qna']:
                st.text(i)
            if submitted and user_input:
                placeholder = st.empty()
                placeholder.text("bot: typing...")
                try:
                    res = research_llm.run(input=user_input)
                except ValueError as e:
                    res = research_llm.run(input=user_input)
                st.session_state['research_qna'].append(f"bot: {res}\n")
                placeholder.empty()
                st.text(f"bot: {res}\n")
    with hc:
        question_container = st.container()
        result_container = st.container()
        
        with question_container:
            with st.form("hc_form", clear_on_submit=True):
                "bot: Hi, I am Wealthsimple's trusted AI agent! I can answer all WS related questions."
                user_input = st.text_input("type in your questions: ", key='hc_q')
                submitted = st.form_submit_button("Submit")
                if submitted and user_input:
                    st.session_state['hc_qna'].append(f"user: {user_input}")

        with result_container:
            for i in st.session_state['hc_qna']:
                st.text(i)
            if submitted and user_input:
                placeholder = st.empty()
                placeholder.text("bot: typing...")
                try:
                    res = hc_llm.run(input=user_input)
                except ValueError as e:
                    res = hc_llm.run(input=user_input)
                st.session_state['hc_qna'].append(f"bot: {res}\n")
                placeholder.empty()
                st.text(f"bot: {res}\n")