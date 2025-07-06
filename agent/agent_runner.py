from langchain.agents import create_tool_calling_agent
from langchain_core.agents import AgentAction, AgentFinish
from agent.prompts import system_prompt, user_prompt
from agent.tools import get_tools

from langchain.prompts import ChatPromptTemplate

def get_agent(llm):
    tools = get_tools()
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
        ("placeholder", "{agent_scratchpad}")
    ])
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )
    return agent, tools


def run_agent_with_tools(agent, user_input, tools):
    intermediate_steps = []
    input_dict = {"input": user_input, "intermediate_steps": intermediate_steps}
    response = agent.invoke(input_dict)
    while (isinstance(response, list) and response and isinstance(response[0], AgentAction)) or isinstance(response, AgentAction):
        if isinstance(response, list):
            action = response[0]
        else:
            action = response
        tool_name = action.tool
        tool_input = action.tool_input
        tool = next((t for t in tools if t.name.lower() == tool_name.lower()), None)
        if tool is None:
            tool = next((t for t in tools if tool_name.lower() in t.name.lower()), None)
        if tool is None:
            tool_result = f"Tool {tool_name} not found."
        else:
            try:
                if hasattr(tool, "run"):
                    tool_result = tool.run(tool_input)
                elif hasattr(tool, "invoke"):
                    tool_result = tool.invoke(tool_input)
                else:
                    tool_result = tool(tool_input)
            except Exception as e:
                tool_result = f"Tool {tool_name} error: {e}"
        if isinstance(tool_result, dict):
            answer = tool_result.get("answer", str(tool_result))
            tool_used = tool_result.get("tool", "Unknown")
            citations = tool_result.get("citations", [])
            tool_result = {
                "answer": answer,
                "tool": tool_used,
                "citations": citations
            }
        else:
            answer = str(tool_result)
            tool_used = action.tool if hasattr(action, 'tool') else "Unknown"
            citations = []
            tool_result = {
                "answer": answer,
                "tool": tool_used,
                "citations": citations
            }
        intermediate_steps.append((action, tool_result))
        response = agent.invoke({"input": user_input, "intermediate_steps": intermediate_steps})
    final_answer = None
    tool_used = None
    citations = []
    if isinstance(response, list) and response:
        if isinstance(response[0], AgentFinish):
            agent_finish = response[0]
            output = agent_finish.return_values
            if isinstance(output, dict) and "output" in output:
                final_answer = output["output"]
            else:
                final_answer = str(output)
        else:
            final_answer = str(response)
    elif isinstance(response, AgentFinish):
        output = response.return_values
        if isinstance(output, dict) and "output" in output:
            final_answer = output["output"]
        else:
            final_answer = str(output)
    elif isinstance(response, dict) and "output" in response:
        final_answer = response["output"]
    elif not isinstance(response, list) and not isinstance(response, dict) and hasattr(response, "return_values") and isinstance(response.return_values, dict) and "output" in response.return_values:
        final_answer = response.return_values["output"]
    else:
        final_answer = str(response)
    if intermediate_steps:
        last_tool_result = intermediate_steps[-1][1]
        if isinstance(last_tool_result, dict):
            tool_used = last_tool_result.get("tool", None)
            citations = last_tool_result.get("citations", [])

    tool_display_names = {
        "RAG": "Internal HR Policy Search",
        "WebSearch": "Web Search",
        "InsuranceQuery": "Insurance Policy Search",
        "InsuranceDocument": "Insurance Document Retrieval"
    }

    display = final_answer if isinstance(final_answer, str) else str(final_answer)
    if citations:
        display += "\n\n**References:**\n" + "\n".join(f"- {c}" for c in citations)
    if tool_used:
        friendly_name = tool_display_names.get(tool_used, tool_used)
        display += f"\n\n_Source: {friendly_name}_"
    return display