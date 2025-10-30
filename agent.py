from strands import Agent
from strands_tools import calculator, current_time

agent = Agent(tools=[calculator, current_time], load_tools_from_directory=True)

while True:
    agent(input("\n# "))
