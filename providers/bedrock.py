from langchain_aws import ChatBedrockConverse

def get_llm():
    return ChatBedrockConverse(model="anthropic.claude-3-sonnet-20240229-v1:0")