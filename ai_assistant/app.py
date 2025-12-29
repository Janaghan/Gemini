from dotenv import load_dotenv

# Load environment variables (from .env in current or parent dir)
load_dotenv()

import os
from flask import Flask, render_template, jsonify, request
from google import genai
from src.session import create_ephemeral_token, require_token, TOKEN_TTL_SECONDS, GEMINI_API_KEY

from flask_sock import Sock
import websockets
import asyncio
import json

app = Flask(__name__)
sock = Sock(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/token", methods=["POST"])
def get_ephemeral_token():
    """
    Issues a LOCAL JWT for the frontend to connect to our backend proxy.
    """
    try:
        # Generate our internal JWT
        token = create_ephemeral_token()
        is_fallback = False 
        
        return jsonify({
            "token": token,
            "expires_in": TOKEN_TTL_SECONDS
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sock.route('/ws_stream')
def ws_stream(ws):
    """
    WebSocket Proxy:
    Client --(Local JWT)--> Backend --(API Key)--> Gemini Live
    """
    # 1. Authenticate
    token = request.args.get('token')
    if not token:
        ws.close(1008, "Missing Token")
        return
    try:
        require_token(token)
    except PermissionError:
        ws.close(1008, "Invalid Token")
        return

    print("DEBUG: Proxy Client Authenticated. Connecting to Gemini...")

    # 2. Connect to Gemini Live (as the Backend)
    # Use standard API Key here.
    # Note: 'key' param works fine in backend-to-backend context usually, or we use 'x-goog-api-key' header if needed.
    # We will use the URL with ?key= first.
    GEMINI_URL = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"
    
    # We need a synchronous wrapper for the async websockets library since Flask handles requests in threads (usually).
    # However, flask-sock runs in a thread. 'websockets' is async.
    # We can use 'asyncio.run' to run the proxy loop, but we need to supply an async function.
    
    async def proxy_loop():
        async with websockets.connect(GEMINI_URL) as gemini_ws:
            print("DEBUG: Backend connected to Gemini Live.")
            
            # Tasks for bidirectional forwarding
            async def client_to_gemini():
                try:
                    while True:
                        # flask-sock 'ws.receive()' is blocking/sync. 
                        # We need to run it in a way that doesn't block the async loop?
                        # Actually mixing sync (flask-sock) and async (websockets) is tricky.
                        # Easier: Use 'simple_websocket' style?
                        # Or just use the fact that receive() is a blocking call, so we might need a thread.
                        
                        # LIMITATION: flask-sock is sync. websockets is async.
                        # BETTER APPROACH: Just use run_in_executor for the blocking ws.receive().
                        
                        data = ws.receive() # Blocks
                        if data is None: break # Closed
                        await gemini_ws.send(data)
                except Exception as e:
                    print(f"DEBUG: Client->Gemini Error: {e}")

            async def gemini_to_client():
                try:
                    async for msg in gemini_ws:
                        ws.send(msg) # Blocks? simple-websocket send is sync.
                except Exception as e:
                    print(f"DEBUG: Gemini->Client Error: {e}")

            # Run both
            # Issue: ws.receive() blocks the whole thread.
            # We can't easily run both in one asyncio loop if one input is blocking sync.
            # We will use a separate thread for Client->Gemini.
            pass
            
            # RE-THINK: It is easier to write a simple sync loop using 'websocket-client' (sync) instead of 'websockets' (async) for the backend connection?
            # OR use asyncio.to_thread for the sync Flask-Sock calls.
            
            loop = asyncio.get_running_loop()
            
            # Task 1: Forward Gemini -> Client (Async source -> Sync destination)
            t1 = asyncio.create_task(gemini_to_client())
            
            # Task 2: Forward Client -> Gemini (Sync source -> Async destination)
            # We must use run_in_executor to not block the loop
            while True:
                try:
                    data = await loop.run_in_executor(None, ws.receive)
                    if data is None: 
                        break
                    await gemini_ws.send(data)
                except Exception:
                    break
            
            t1.cancel()

    try:
        asyncio.run(proxy_loop())
    except Exception as e:
        print(f"DEBUG: Proxy Loop Error: {e}")
        ws.close(1011, "Proxy Error")
    print("DEBUG: Proxy Closed")

@app.route("/extract_pdf", methods=["POST"])
def extract_pdf():
    """
    Extracts text from uploaded PDF.
    REQUIRES a valid ephemeral token.
    """

    # 1. Validate token
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401

    token = auth.split(" ", 1)[1]

    try:
        require_token(token)
    except Exception:
        return jsonify({"error": "Invalid or expired token"}), 401

    # 2. Handle PDF
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        import pypdf
        reader = pypdf.PdfReader(file)
        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": f"PDF reading failed: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
