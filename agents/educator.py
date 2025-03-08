import re
from models import State
from config import llm
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults


summary_template = """
Summarize the following content into a concise paragraph that directly addresses the query. Ensure the summary 
highlights the key points relevant to the query while maintaining clarity and completeness.
Query: {query}
Content: {content}
"""

def search_web(state: State):
    search = TavilySearchResults(max_results=3)
    search_results = search.invoke(state["question"])

    state["sources"] = [result['url'] for result in search_results]
    state["web_results"] = [result['content'] for result in search_results]

    return state

def clean_text(text: str):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

def summarize_results(state: State):
    prompt = ChatPromptTemplate.from_template(summary_template)
    chain = prompt | llm

    summarized_results = []
    for content in state["web_results"]:
        summary = chain.invoke({"query": state["question"], "content": content})
        clean_content = clean_text(summary.content)
        summarized_results.append(clean_content)
    
    state["summarized_results"] = summarized_results

    return state


