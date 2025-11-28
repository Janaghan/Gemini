import time
import json
import argparse
from google.genai import types
from config import client
from log_setup import start_span, end_span, laminar_event
from tools import tools

SYSTEM_INSTRUCTIONS = """You are an intelligent and helpful AI assistant.

**Capabilities:**
1.  **Reasoning:** You can think deeply about complex problems. If a thinking budget is provided, use it to plan your response.
2.  **Tools:** You have access to external tools, specifically `get_air_quality` for checking air quality.
3.  **Conversation:** You can engage in multi-turn conversations.

**Guidelines:**
-   **Air Quality:** When asked about air quality, ALWAYS use the `get_air_quality` tool. Do not guess.
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


args = parser()


def Text_bot(prompt):

    model = "gemini-2.5-flash"
    span_id = start_span("gemini_request")
    start_time = time.time()

    laminar_event("request_start", span_id, {
        "prompt": prompt,
        "thinking_budget": args.thinking_budget,
        "mode": (
            "function_call" if args.function_calling
            else "multichat" if args.multichat
            else "normal"
        )
    })

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
                        laminar_event("function_call_detected", span_id, {
                            "name": fn.name,
                            "args": fn.args
                        })

        # 2. Check for manual function call (if auto-execution didn't happen or was disabled)
        function_call_part = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                function_call_part = part
                break

        if function_call_part:
           
            fn = function_call_part.function_call
            laminar_event("function_call_detected", span_id, {
                "name": fn.name,
                "args": fn.args
            })

            # Find the function in the tools list
            target_tool = next((t for t in tools if t.__name__ == fn.name), None)

            if target_tool:
                try:
                    result = target_tool(**fn.args)
                    reply = f"Function executed: {result}"
                except Exception as e:
                    reply = f"Error executing function {fn.name}: {e}"
            else:
                reply = f"Unknown function called: {fn.name}"

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
                # For now, just notify user that tool use is detected but not fully implemented in this simple loop
                # Or better, implement simple tool execution here too, or just let it print the function call
                fn = function_call_part.function_call
                reply_text = f"[Tool Call: {fn.name}({fn.args})]"
                
                # Execute tool if possible (simple version)
                target_tool = next((t for t in tools if t.__name__ == fn.name), None)
                if target_tool:
                    try:
                        result = target_tool(**fn.args)
                        reply_text += f"\nResult: {result}"
                        # Append tool response to history so model knows
                        # (Skipping full tool response integration for brevity, just showing result)
                    except Exception as e:
                        reply_text += f"\nError: {e}"

            else:
                reply_text = "".join(
                    p.text for p in model_reply.parts if hasattr(p, "text")
                )

            history.append(model_reply)

            laminar_event("multichat_turn", span_id, {
                "user": user_msg,
                "model": reply_text
            })

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

    latency_ms = round((time.time() - start_time) * 1000, 2)

    laminar_event("response_end", span_id, {
        "response_text": reply,
        "latency_ms": latency_ms
    })

    end_span(span_id, {"latency_ms": latency_ms})
    return reply



if args.multichat:
    answer = Text_bot(prompt=None)
    print("Answer:", answer)
else:
    prompt = input("Enter your prompt: ")
    answer = Text_bot(prompt)
    print("Answer:", answer)
    