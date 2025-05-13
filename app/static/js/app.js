/**
 * app.js: JS code for the adk-streaming sample app.
 */

/**
 * WebSocket handling
 */

// Global variables
const sessionId = Math.random().toString().substring(10);
const ws_url = "ws://" + window.location.host + "/ws/" + sessionId;
let websocket = null;
let is_audio = false;

// Get DOM elements
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
const statusDot = document.getElementById("status-dot");
const connectionStatus = document.getElementById("connection-status");
const typingIndicator = document.getElementById("typing-indicator");
const startAudioButton = document.getElementById("startAudioButton");
const stopAudioButton = document.getElementById("stopAudioButton");
const recordingContainer = document.getElementById("recording-container");
let currentMessageId = null;

// WebSocket handlers
function connectWebsocket() {
  // Connect websocket
  const wsUrl = ws_url + "?is_audio=" + is_audio;
  websocket = new WebSocket(wsUrl);

  // Handle connection open
  websocket.onopen = function () {
    // Connection opened messages
    console.log("WebSocket connection opened.");
    connectionStatus.textContent = "Connected";
    statusDot.classList.add("connected");

    // Enable the Send button
    document.getElementById("sendButton").disabled = false;
    addSubmitHandler();
  };

  // Handle incoming messages
  websocket.onmessage = function (event) {
    // Parse the incoming message
    const message_from_server = JSON.parse(event.data);
    console.log("[AGENT TO CLIENT] ", message_from_server);

    // Show typing indicator when response starts
    if (!currentMessageId && !message_from_server.turn_complete) {
      typingIndicator.classList.add("visible");
    }

    // Check if the turn is complete
    // if turn complete, add new message
    if (
      message_from_server.turn_complete &&
      message_from_server.turn_complete == true
    ) {
      currentMessageId = null;
      typingIndicator.classList.remove("visible");
      return;
    }

    // If it's audio, play it (but don't remove the text that might be displayed)
    if (message_from_server.mime_type == "audio/pcm" && audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));

      // If we have audio and a text message already being displayed, mark it with an audio icon if not already done
      if (currentMessageId && is_audio) {
        const message = document.getElementById(currentMessageId);
        if (message && !message.querySelector(".audio-icon")) {
          // Add audio icon to the message
          const audioIcon = document.createElement("span");
          audioIcon.className = "audio-icon";
          message.prepend(audioIcon);
        }
      }
    }

    // If it's a text, print it
    if (message_from_server.mime_type == "text/plain") {
      // Hide typing indicator when we start receiving text
      typingIndicator.classList.remove("visible");

      // add a new message for a new turn
      if (currentMessageId == null) {
        currentMessageId = Math.random().toString(36).substring(7);
        const message = document.createElement("p");
        message.id = currentMessageId;
        message.className = "agent-message";

        // If audio is enabled, add the audio icon
        if (is_audio) {
          const audioIcon = document.createElement("span");
          audioIcon.className = "audio-icon";
          message.appendChild(audioIcon);
        }

        // Append the message element to the messagesDiv
        messagesDiv.appendChild(message);
      }

      // Add message text to the existing message element
      const message = document.getElementById(currentMessageId);

      // Get the text node or create one if it doesn't exist
      let textNode = Array.from(message.childNodes).find(
        (node) => node.nodeType === Node.TEXT_NODE
      );
      if (!textNode) {
        textNode = document.createTextNode("");
        message.appendChild(textNode);
      }

      // Update the text
      textNode.nodeValue =
        (textNode.nodeValue || "") + message_from_server.data;

      // Scroll down to the bottom of the messagesDiv
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  };

  // Handle connection close
  websocket.onclose = function () {
    console.log("WebSocket connection closed.");
    document.getElementById("sendButton").disabled = true;
    connectionStatus.textContent = "Disconnected. Reconnecting...";
    statusDot.classList.remove("connected");
    typingIndicator.classList.remove("visible");
    setTimeout(function () {
      console.log("Reconnecting...");
      connectWebsocket();
    }, 5000);
  };

  websocket.onerror = function (e) {
    console.log("WebSocket error: ", e);
    connectionStatus.textContent = "Connection error";
    statusDot.classList.remove("connected");
    typingIndicator.classList.remove("visible");
  };
}
connectWebsocket();

// Add submit handler to the form
function addSubmitHandler() {
  messageForm.onsubmit = function (e) {
    e.preventDefault();
    const message = messageInput.value;
    if (message) {
      const p = document.createElement("p");
      p.textContent = message;
      p.className = "user-message";
      messagesDiv.appendChild(p);
      messageInput.value = "";

      // Show typing indicator after sending message
      typingIndicator.classList.add("visible");

      sendMessage({
        mime_type: "text/plain",
        data: message,
      });
      console.log("[CLIENT TO AGENT] " + message);
      // Scroll down to the bottom of the messagesDiv
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    return false;
  };
}

// Send a message to the server as a JSON string
function sendMessage(message) {
  if (websocket && websocket.readyState == WebSocket.OPEN) {
    const messageJson = JSON.stringify(message);
    websocket.send(messageJson);
  }
}

// Decode Base64 data to Array
function base64ToArray(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Audio handling
 */

let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;
let isRecording = false;

// Import the audio worklets
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

// Start audio
function startAudio() {
  // Start audio output
  startAudioPlayerWorklet().then(([node, ctx]) => {
    audioPlayerNode = node;
    audioPlayerContext = ctx;
  });
  // Start audio input
  startAudioRecorderWorklet(audioRecorderHandler).then(
    ([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
      isRecording = true;
    }
  );
}

// Stop audio recording
function stopAudio() {
  if (audioRecorderNode) {
    audioRecorderNode.disconnect();
    audioRecorderNode = null;
  }

  if (audioRecorderContext) {
    audioRecorderContext
      .close()
      .catch((err) => console.error("Error closing audio context:", err));
    audioRecorderContext = null;
  }

  if (micStream) {
    micStream.getTracks().forEach((track) => track.stop());
    micStream = null;
  }

  isRecording = false;
}

// Start the audio only when the user clicked the button
// (due to the gesture requirement for the Web Audio API)
startAudioButton.addEventListener("click", () => {
  startAudioButton.disabled = true;
  startAudioButton.textContent = "Voice Enabled";
  startAudioButton.style.display = "none";
  stopAudioButton.style.display = "inline-block";
  recordingContainer.style.display = "flex";
  startAudio();
  is_audio = true;

  // Add class to messages container to enable audio styling
  messagesDiv.classList.add("audio-enabled");

  connectWebsocket(); // reconnect with the audio mode
});

// Stop audio recording when stop button is clicked
stopAudioButton.addEventListener("click", () => {
  stopAudio();
  stopAudioButton.style.display = "none";
  startAudioButton.style.display = "inline-block";
  startAudioButton.disabled = false;
  startAudioButton.textContent = "Enable Voice";
  recordingContainer.style.display = "none";

  // Remove audio styling class
  messagesDiv.classList.remove("audio-enabled");

  // Reconnect without audio mode
  is_audio = false;

  // Only reconnect if the connection is still open
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.close();
    // The onclose handler will trigger reconnection
  }
});

// Audio recorder handler
function audioRecorderHandler(pcmData) {
  // Only send data if we're still recording
  if (!isRecording) return;

  // Send the pcm data as base64
  sendMessage({
    mime_type: "audio/pcm",
    data: arrayBufferToBase64(pcmData),
  });

  // Log every few samples to avoid flooding the console
  if (Math.random() < 0.01) {
    // Only log ~1% of audio chunks
    console.log("[CLIENT TO AGENT] sent audio data");
  }
}

// Encode an array buffer with Base64
function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}
