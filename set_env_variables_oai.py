import getpass
import os

# Prompt for Azure OpenAI API key
os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass("Enter your Azure OpenAI API key: ")

# Prompt for Azure OpenAI endpoint
os.environ["AZURE_OPENAI_ENDPOINT"] = input("Enter your Azure OpenAI endpoint: ")
