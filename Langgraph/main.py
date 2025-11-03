from typing import TypedDict
from typing_extensions import Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
import wikipedia
from dotenv import load_dotenv
from pydantic import BaseModel
import json

load_dotenv()


# ------------------ STATE ------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ------------------ RESPONSE FORMAT ------------------
class MessagesResponseFormat(BaseModel):
    returns: bool


# Create a parser that forces the LLM to return this format
parser = PydanticOutputParser(pydantic_object=MessagesResponseFormat)

prompt = PromptTemplate(
    template=(
        "You are a difficulty evaluator.\n"
        "Return a JSON object with key `returns`.\n"
        "- `returns` should be true if the question is difficult.\n"
        "- `returns` should be false if the question is simple.\n\n"
        "Question: {question}\n\n"
        "Response format:\n{format_instructions}"
    ),
    input_variables=["question"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# --------------------BOT TOOLS------------------
@tool
def search_wikipedia_tool(query):
    """Searches Wikipedia for a given query and returns a summary."""
    try:
        results = wikipedia.search(query)
        if not results:
            return "No results found."
        
        page = wikipedia.page(results[0])
        summary = wikipedia.summary(page.title, sentences=4)
        return f"Title: {page.title}\n\nSummary: {summary}"
    except wikipedia.DisambiguationError as e:
        return f"Too many results. Try one of these: {e.options[:5]}"
    except wikipedia.PageError:
        return "Page not found."
    except Exception as e:
        return f"Error: {str(e)}"


       


# ------------------ BOT NODE ------------------
def RoutingQuery(state: State):
    llm_model = init_chat_model(
        model_provider='google_genai',
        model="gemini-2.5-flash-lite"
    )

    user_message = state["messages"][-1].content
    response = llm_model.invoke(
        prompt.format(question=user_message)
    )
    parsed = parser.parse(response.content)
    print("Parsed output:", parsed)
    next_node = "easyQueryNode" if not parsed.returns else "toughQueryNode"
    return {
        "messages": state["messages"] + [{"role": "assistant", "content": f"Routing to {next_node}"}],
        "next": next_node
    }


def easyQueryNode(state: State):
    llm_model = init_chat_model(
        model_provider='google_genai',
        model="gemini-2.5-flash-lite",
    )

    response = llm_model.invoke(
        state['messages']
    )

    # Append response as a chat message
    return {'messages': [{'role': 'assistant', 'content': response.content}]}

def toughQueryNode(state: State):
    llm_model = init_chat_model(
        model_provider='google_genai',
        model="gemini-2.5-flash",
        tools=[search_wikipedia_tool],)

    response = llm_model.invoke(
        state['messages']
    )

    # Append response as a chat message
    return {'messages': [{'role': 'assistant', 'content': response.content}]}

# ------------------ GRAPH BUILDING ------------------

graph_builder = StateGraph(State)
graph_builder.add_node("RoutingQuery", RoutingQuery)
graph_builder.add_node("easyQueryNode", easyQueryNode)
graph_builder.add_node("toughQueryNode", toughQueryNode)

graph_builder.add_edge(START, "RoutingQuery")


graph_builder.add_conditional_edges(
    "RoutingQuery",
    lambda output: output['next'],  # determines which edge to follow
    {
        "easyQueryNode": "easyQueryNode",
        "toughQueryNode": "toughQueryNode",
    }
)

graph_builder.add_edge("easyQueryNode", END)
graph_builder.add_edge("toughQueryNode", END)

graph = graph_builder.compile()


# ------------------ RUN LOOP ------------------
def runChat(query):

        SYSTEM_PROMPT = """“
        You are a concise assistant. Always answer in under 50 words.
Only exceed 50 words if absolutely necessary for correctness or safety.
Focus on key information, avoid filler, and give short, direct responses.”

Examples (Few-shot):

User: What is photosynthesis?
Assistant: Plants convert sunlight, water, and carbon dioxide into glucose and oxygen. It’s how they make energy.

User: Explain Newton’s third law.
Assistant: Every action has an equal and opposite reaction. Forces come in pairs.

User: Summarize the causes of World War I.
Assistant: Militarism, alliances, imperialism, and nationalism created tension. The assassination of Archduke Franz Ferdinand triggered the war.

User: Describe AI in simple words.
Assistant: AI lets computers learn patterns and make decisions like humans, often using data and algorithms."""
        response = graph.invoke({
            "messages": [{'role': 'system', 'content': SYSTEM_PROMPT}
                ,{"role": "user", "content": query},]
        })

        return response['messages'][-1].content



