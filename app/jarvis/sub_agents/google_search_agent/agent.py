from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

GoogleSearchAgent = Agent(
    # A unique name for the agent.
    name="google_search_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash-exp",
    # A short description of the agent's purpose.
    description="Agent to answer questions using Google Search.",
    # Instructions to set the agent's behavior.
    instruction="You are an expert researcher. You always stick to the facts. Make sure you answer the questions as concisely as possible. Answer the question and don't provide any additional information.",
    # Add google_search tool to perform grounding with Google search.
    tools=[google_search],
)
