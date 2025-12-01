import time
import json
import argparse
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from lmnr import Laminar
from log_setup import start_span, end_span, observe
from tools import tools
load_dotenv()
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))
SYSTEM_INSTRUCTIONS = """You are an intelligent and helpful AI assistant.

**Capabilities:**
1.  **Reasoning:** You can think deeply about complex problems. If a thinking budget is provided, use it to plan your response.
2.  **Tools:** You have access to external tools, specifically `get_air_quality` for checking air quality.
3.  **Conversation:** You can engage in multi-turn conversations.

**Guidelines:**
-   **Air Quality:** You can answer general questions about air quality (definitions, pollutants, health effects) directly. Use the `get_air_quality` tool ONLY when the user asks for real-time data or specific location information.
-   **Thinking:** If `thinking_budget` > 0, use your thinking process to analyze the user's intent and verify your plan before executing tools or answering.
-   **Tone:** Be professional, concise, and friendly.
-   **Fallback:** If a tool fails or returns no data, explain the situation clearly to the user and suggest alternatives if possible.
"""

def parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--thinking_budget', type=int, default=1,
                        help='Thinking budget for Gemini')

    parser.add_argument('-f', '--function_calling', action='store_true',
                        help='Enable function calling')

    parser.add_argument('-m', '--multichat', action='store_true',
                        help='Enable multi-turn chat')

    return parser.parse_args()


@observe("tool_execution")
def execute_tool(tool_name: str, tool_args: dict) -> str:
    """Execute a tool by name with given arguments."""
    target_tool = next((t for t in tools if t.__name__ == tool_name), None)

    if not target_tool:
        return f"Unknown function called: {tool_name}"

    try:
        result = target_tool(**tool_args)
        return f"Function executed: {result}"
    except Exception as e:
        return f"Error executing function {tool_name}: {e}"


args = parser()


@observe("gemini_request")
def Text_bot(prompt):

    model = "gemini-2.5-flash"

    if args.function_calling:
        # Use the tools imported from tools.py
        # tools is already a list of functions, which the SDK supports
        
        contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=tools,
                system_instruction=SYSTEM_INSTRUCTIONS
            )
        )

        # 1. Check for automatic function calls (SDK handled)
        if hasattr(response, "automatic_function_calling_history") and response.automatic_function_calling_history:
            for content in response.automatic_function_calling_history:
                for part in content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fn = part.function_call

        # 2. Check for manual function call (if auto-execution didn't happen or was disabled)
        function_call_part = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                function_call_part = part
                break

        if function_call_part:
           
            fn = function_call_part.function_call
            reply = execute_tool(fn.name, fn.args)

        else:
            
            reply = response.text or ""


    elif args.multichat:

        history = []
        print("Multichat started. Type 'exit' to quit.\n")

        while True:
            user_msg = input("You: ")
            if user_msg.lower() in ["exit", "quit"]:
                print("Exiting multichat.\n")
                break

            history.append(types.Content(
                role="user", parts=[types.Part(text=user_msg)]
            ))

            response = client.models.generate_content(
                model=model,
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS,
                    tools=tools # Enable tools in multichat as well
                )
            )

            if not response.candidates or not response.candidates[0].content:
                print("Gemini: (No response content. Likely blocked or empty.)\n")
                continue

            model_reply = response.candidates[0].content
            
            # Handle function calls in multichat if they occur
            function_call_part = None
            for part in model_reply.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call_part = part
                    break
            
            if function_call_part:
                fn = function_call_part.function_call
                reply_text = execute_tool(fn.name, fn.args)

            else:
                reply_text = "".join(
                    p.text for p in model_reply.parts if hasattr(p, "text")
                )

            history.append(model_reply)

            # multichat turn observed by the surrounding gemini_request decorator

            print(f"Gemini: {reply_text}\n")

        end_span(span_id)
        return ""

    else:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config= types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=args.thinking_budget
                ),
                system_instruction=SYSTEM_INSTRUCTIONS
            )
            # metadata={"laminar_span_id": span_id}
        )

        reply = response.text or ""

    return reply



if args.multichat:
    answer = Text_bot(prompt=None)
    print("Answer:", answer)
else:
    prompt = input("Enter your prompt: ")
    answer = Text_bot(prompt)
    print("Answer:", answer)
    