import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.utilities import PythonREPL
from langchain.agents import Tool, create_pandas_dataframe_agent, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders.duckdb_loader import DuckDBLoader
from langchain.indexes import VectorstoreIndexCreator
import openai
import duckdb
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_RSI(price, lookback=14):
    change = price.copy().diff()
    change.dropna(inplace=True)

    change_up = change.copy()
    change_down = change.copy()

    change_up[change_up<0] = 0
    change_down[change_down>0] = 0

    # Calculate the rolling average of average up and average down
    avg_up = change_up.rolling(lookback).mean()
    avg_down = change_down.rolling(lookback).mean().abs()
    rsi = 100 * avg_up / (avg_up + avg_down)
    return rsi

def get_sma(price, lookback):
    """referenced from vectorize me slides"""
    sma = price.rolling(window=lookback, min_periods=lookback).mean()
    return sma

def get_golden_or_death_cross(price, golden, return_sma=False):
    short_lookback = 10
    long_lookback = 30
    sma_short = get_sma(price, short_lookback)
    sma_long = get_sma(price, long_lookback)
    sma = sma_short.join(sma_long, lsuffix=f'_SMA_{short_lookback}', rsuffix=f'_SMA_{long_lookback}')
    sma.rename(columns={
        f'Close_SMA_{short_lookback}':f'SMA_{short_lookback}',
        f'Close_SMA_{long_lookback}':f'SMA_{long_lookback}',
    }, inplace=True)
    
    if golden:
        crossed = sma[f'SMA_{short_lookback}'] > sma[f'SMA_{long_lookback}']
    else:
        crossed = sma[f'SMA_{short_lookback}'] < sma[f'SMA_{long_lookback}']

    to_modify=[]
    for i in range(1, len(crossed)):
        if crossed.iloc[i-1] and crossed.iloc[i]:
            to_modify.append(i)
    crossed.iloc[to_modify] = False

    if return_sma:
        return crossed, sma
    return crossed

def get_data():
    sp500 = pd.read_csv('data/sp500.csv', index_col='Date')
    spy = pd.read_csv('data/sp500_index.csv', index_col='Date')
    spy['Ticker'] = 'SPY'
    spy.columns=['Close','Ticker']

    min_date, max_date = max(spy.index.min(), sp500.index.min()), min(spy.index.max(), sp500.index.max())
    dates = pd.DataFrame(index=pd.date_range(min_date, max_date))
    dates.index = dates.index.rename('Date').astype(str)

    sp500 = dates.join(sp500, how='left').fillna(method="ffill").fillna(method="bfill").sort_index(axis=0)
    spy = dates.join(spy, how='left').fillna(method="ffill").fillna(method="bfill").sort_index(axis=0)
    df = pd.concat([sp500, spy])

    new_dfs = []
    for idx, symbol in enumerate(df.Ticker.unique()):
        if idx % 10 == 0:
            print(f"{idx+1} / {len(df.Ticker.unique())} tickers")
        symbol_df = df[df.Ticker==symbol].reset_index()
        symbol_df.loc[:,'rsi'] = get_RSI(symbol_df[['Close']], 14)
        golden_cross,sma = get_golden_or_death_cross(symbol_df[['Close']], golden=True, return_sma=True)
        death_cross = get_golden_or_death_cross(symbol_df[['Close']], golden=False, return_sma=False)
        symbol_df.loc[:,'golden_cross'] = [1 if i else 0 for i in golden_cross]
        symbol_df.loc[:,'death_cross'] = [1 if i else 0 for i in death_cross] 
        symbol_df = symbol_df.join(sma, how='left')
        symbol_df.set_index('Date', inplace=True)
        new_dfs.append(symbol_df)

    df=pd.concat(new_dfs).reset_index()
    return df

@st.cache_resource
def get_research_agent():
    # llm = OpenAI(temperature=0)
    llm = ChatOpenAI(model_name='gpt-4', temperature=0)
    python_repl = PythonREPL()
    agent = create_pandas_dataframe_agent(llm, get_data(), verbose=True)
    tools = [
        Tool(
            name="Python REPL",
            func=python_repl.run,
            description="A Python shell. Use this to execute python commands. Input should be a valid python command."
        ),
        Tool(
            name="Stock data",
            func=agent.run,
            description="useful for anything related to stock information"
        )
    ]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm_chain = initialize_agent(tools=tools, llm=llm, agent="chat-conversational-react-description", memory=memory, verbose=True)
    return llm_chain

@st.cache_resource
def get_hc_agent():
    llm = ChatOpenAI(model_name='gpt-4', temperature=0)
    con = duckdb.connect('llm_demo.db')
    try:
        con.sql("SELECT * from hc_articles limit 1")
    except duckdb.CatalogException:
        hc_articles = pd.read_csv('data/active_hc_articles.csv', usecols=['id','html_url','title','body'])
        con.sql("DROP TABLE IF EXISTS hc_articles")
        con.sql("CREATE TABLE hc_articles as select * from hc_articles")

    loader = DuckDBLoader("SELECT * FROM hc_articles", database="llm_demo.db")
    index = VectorstoreIndexCreator().from_loaders([loader])
    tools = [
        Tool(
            name="Help center",
            func=index.query,
            description="useful for helping the user"
        )
    ]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm_chain = initialize_agent(tools=tools, llm=llm, agent="chat-conversational-react-description", memory=memory, verbose=True)
    return llm_chain


research_llm = get_research_agent()
hc_llm = get_hc_agent()