from strands import Agent
from strands_tools import calculator, current_time
from tools import speech_to_speech, voice_chat_server

agent = Agent(tools=[calculator, current_time, voice_chat_server])

while True:
    agent(input("\n# "))
