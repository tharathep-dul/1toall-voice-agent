import asyncio
import base64
import json
import os
import traceback
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from jarvis.tools.calendar_tools import (
    create_event,
    delete_event,
    find_free_time,
    list_calendars,
    list_events,
)

from app.jarvis.agent import root_agent

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "ADK Streaming example"
session_service = InMemorySessionService()


def start_agent_session(session_id, is_audio=False):
    """Starts an agent session"""

    # Create a Session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"

    # Create speech config with voice settings
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            # Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, and Zephyr
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    )

    # Create run config with basic settings
    run_config = RunConfig(response_modalities=[modality], speech_config=speech_config)

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket, live_events, live_request_queue):
    """Agent to client communication"""
    while True:
        async for event in live_events:

            # If the turn complete or interrupted, send it
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: {message}")
                continue

            print("[AGENT TO CLIENT EVENT]:", event)
            print("[AGENT TO CLIENT EVENT TYPE]:", type(event))

            # Handle function calls - first check if there are tool_calls directly on the event
            tool_calls = getattr(event, "tool_calls", None)
            print("[TOOL_CALLS]:", tool_calls)

            # If no tool_calls directly, check for function_call in the content parts
            if not tool_calls and hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    function_call = getattr(part, "function_call", None)
                    if function_call:
                        print("[FUNCTION_CALL IN CONTENT]:", function_call)
                        tool_calls = [function_call]
                        break

            # Process any tool calls we found
            if tool_calls:
                print(f"[FOUND TOOL CALLS]: {tool_calls}")
                function_responses = []

                for tool_call in tool_calls:
                    print("[PROCESSING TOOL CALL]:", tool_call)
                    try:
                        # Extract information as safely as possible
                        # First try direct attribute access
                        func_name = getattr(tool_call, "name", None)
                        func_args = getattr(tool_call, "args", None)
                        func_id = getattr(tool_call, "id", None)

                        # If we have a nested function_call object, use that instead
                        if hasattr(tool_call, "function_call"):
                            print("[NESTED FUNCTION_CALL FOUND]")
                            func_name = getattr(
                                tool_call.function_call, "name", func_name
                            )
                            func_args = getattr(
                                tool_call.function_call, "args", func_args
                            )
                            func_id = getattr(tool_call.function_call, "id", func_id)

                        # Fallbacks if we couldn't get the values
                        if func_name is None:
                            # Try dictionary-style access
                            try:
                                func_name = tool_call.get("name", "unknown_function")
                            except:
                                func_name = "unknown_function"

                        if func_args is None:
                            # Try dictionary-style access
                            try:
                                func_args = tool_call.get("args", {})
                            except:
                                func_args = {}

                        if func_id is None:
                            # Try dictionary-style access
                            try:
                                func_id = tool_call.get("id", "unknown_id")
                            except:
                                func_id = "unknown_id"

                        print(
                            f"[EXTRACTED FUNCTION]: name={func_name}, id={func_id}, args={func_args}"
                        )

                        # Process args - ensure it's a dictionary
                        if isinstance(func_args, str):
                            try:
                                func_args = json.loads(func_args)
                            except:
                                print(
                                    f"[WARNING] Failed to parse args string: {func_args}"
                                )
                                func_args = {}

                        if not isinstance(func_args, dict):
                            print(f"[WARNING] Args is not a dict: {type(func_args)}")
                            func_args = {}

                        # Map function names to actual functions
                        tools_map = {
                            "list_calendars": list_calendars,
                            "list_events": list_events,
                            "create_event": create_event,
                            "delete_event": delete_event,
                            "find_free_time": find_free_time,
                        }

                        # Execute the function if it exists in our tools map
                        if func_name in tools_map:
                            try:
                                print(f"[EXECUTING]: {func_name}({func_args})")
                                result = tools_map[func_name](**func_args)
                                print(f"[RESULT]: {result}")

                                # Create function response
                                function_response = types.FunctionResponse(
                                    id=func_id, name=func_name, response=result
                                )
                                function_responses.append(function_response)
                            except Exception as e:
                                print(f"[ERROR] Function execution failed: {str(e)}")
                                print(traceback.format_exc())

                                # Create error response
                                function_response = types.FunctionResponse(
                                    id=func_id,
                                    name=func_name,
                                    response={
                                        "status": "error",
                                        "message": f"Error: {str(e)}",
                                    },
                                )
                                function_responses.append(function_response)
                        else:
                            print(f"[ERROR] Unknown function: {func_name}")
                    except Exception as e:
                        print(f"[ERROR] Failed to process tool call: {str(e)}")
                        print(traceback.format_exc())

                # Send function responses if we have any
                if function_responses:
                    try:
                        print(f"[SENDING RESPONSES]: {function_responses}")
                        live_request_queue.send_tool_response(
                            function_responses=function_responses
                        )
                        print("[RESPONSES SENT SUCCESSFULLY]")
                    except Exception as e:
                        print(f"[ERROR] Failed to send responses: {str(e)}")
                        print(traceback.format_exc())

                continue

            # Read the Content and its first Part
            part: types.Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part:
                continue

            # If it's audio, send Base64 encoded audio data
            is_audio = (
                part.inline_data
                and part.inline_data.mime_type
                and part.inline_data.mime_type.startswith("audio/pcm")
            )
            if is_audio:
                audio_data = part.inline_data and part.inline_data.data
                if audio_data:
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_data).decode("ascii"),
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                    continue

            # If it's text and a parial text, send it
            if part.text and event.partial:
                message = {"mime_type": "text/plain", "data": part.text}
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: text/plain: {message}")


async def client_to_agent_messaging(websocket, live_request_queue):
    """Client to agent communication"""
    while True:
        # Decode JSON message
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]

        # Send the message to the agent
        if mime_type == "text/plain":
            # Send a text message
            content = types.Content(
                role="user", parts=[types.Part.from_text(text=data)]
            )
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # Send an audio data
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(
                types.Blob(data=decoded_data, mime_type=mime_type)
            )
        else:
            raise ValueError(f"Mime type not supported: {mime_type}")


#
# FastAPI web app
#

app = FastAPI()

STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    is_audio: str = Query(...),
):
    """Client websocket endpoint"""

    # Wait for client connection
    await websocket.accept()
    print(f"Client #{session_id} connected, audio mode: {is_audio}")

    # Start agent session
    live_events, live_request_queue = start_agent_session(
        session_id, is_audio == "true"
    )

    # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events, live_request_queue)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )
    await asyncio.gather(agent_to_client_task, client_to_agent_task)

    # Disconnected
    print(f"Client #{session_id} disconnected")
