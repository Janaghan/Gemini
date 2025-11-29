import time
import json
import argparse
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from lmnr import Laminar, observe
from tools import tools

load_dotenv()
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

# Create a mapping for easy tool execution
tool_map = {func.__name__: func for func in tools}

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
    parser = argparse.ArgumentParser(description="Gemini Chatbot")
    parser.add_argument('-t', '--thinking_budget', type=int, default=1,
                        help='Thinking budget for Gemini')
    parser.add_argument('--no-tools', action='store_true',
                        help='Disable tools')
    parser.add_argument('-lc', '--long_context', action='store_true',
                        help='Enable long context (Default: Enabled if file exists)')
    return parser.parse_args()

args = parser()

@observe()
def execute_tool(name, args):
    if name in tool_map:
        try:
            print(f"System: Executing tool '{name}' with args: {args}")
            result = tool_map[name](**args)
            return result
        except Exception as e:
            return f"Error executing tool {name}: {e}"
    return f"Error: Tool {name} not found."

@observe()
def chat_session():
    model = "gemini-2.5-flash"
    history = []
    
    # Load context once
    global SYSTEM_INSTRUCTIONS
    try:
        with open("tamilnadu_history.txt", "r") as f:
            history_context = f.read()
        SYSTEM_INSTRUCTIONS += f"\n\nHere is some historical context about Tamil Nadu:\n{history_context}"
        print("System: Loaded Tamil Nadu history context.")
    except FileNotFoundError:
        if args.long_context:
             print("Warning: --long_context requested but tamilnadu_history.txt not found.")
        else:
             print("System: Tamil Nadu history context file not found. Proceeding without it.")

    print("\n--- Gemini Chatbot (Interactive) ---")
    print("Type 'exit' or 'quit' to end the session.")
    
    # Config setup once
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS,
        tools=tools if not args.no_tools else None,
        thinking_config=types.ThinkingConfig(
            thinking_budget=1024
        ) 
    )

    while True:
        try:
            user_msg = input("\nYou: ")
            if user_msg.lower() in ["exit", "quit"]:
                print("Exiting chat. Goodbye!")
                break
            
            history.append(types.Content(
                role="user", parts=[types.Part(text=user_msg)]
            ))
            
            response = client.models.generate_content(
                model=model,
                contents=history,
                config=config
            )

            if not response.candidates or not response.candidates[0].content:
                print("Gemini: (No response content)")
                continue

            model_reply = response.candidates[0].content
            
            # Handle function calls
            function_call_part = None
            for part in model_reply.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call_part = part
                    break
            
            if function_call_part:
                fn = function_call_part.function_call
                tool_result = execute_tool(fn.name, fn.args)
                
                # Send tool result back to model
                func_resp_part = types.Part(
                    function_response=types.FunctionResponse(
                        name=fn.name,
                        response={"result": tool_result} 
                    )
                )
                
                history.append(model_reply) # Add the model's call to history
                
                history.append(types.Content(
                    role="user", 
                    parts=[func_resp_part]
                ))
                
                # Generate again with the tool result
                response2 = client.models.generate_content(
                    model=model,
                    contents=history,
                    config=config
                )
                
                if response2.candidates and response2.candidates[0].content:
                    reply_text = "".join(
                        p.text for p in response2.candidates[0].content.parts if hasattr(p, "text")
                    )
                    history.append(response2.candidates[0].content)
                    print(f"Gemini: {reply_text}")
                else:
                    print("Gemini: (No response after tool execution)")

            else:
                reply_text = "".join(
                    p.text for p in model_reply.parts if hasattr(p, "text")
                )
                history.append(model_reply)
                print(f"Gemini: {reply_text}")

        except KeyboardInterrupt:
            print("\nExiting chat.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    chat_session()
