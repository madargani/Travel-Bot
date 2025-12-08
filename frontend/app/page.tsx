"use client";

import ChatUI from "../components/ChatUI";
import ItineraryDisplay from "../components/ItineraryDisplay";
import { useState, useEffect } from "react";

import { Message, ItineraryProgress } from "../types/Message";

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([
    { user: "assistant", content: "Hello! How can I help you?" },
  ]);
  const [input, setInput] = useState<string>("");
  const [sessionId, setSessionId] = useState<string>("");
  const [itineraryProgress, setItineraryProgress] = useState<ItineraryProgress>(
    {
      stage: "initial",
    },
  );

  // Generate session ID on component mount
  useEffect(() => {
    setSessionId(crypto.randomUUID());
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { user: "user", content: input };
    setMessages([...messages, userMessage]);
    const currentInput = input;
    setInput("");

    // Add assistant message with thinking state
    setMessages((prev) => [
      ...prev,
      { user: "assistant", content: "", isThinking: true },
    ]);

    try {
      // Format message history for backend API
      const messageHistory = messages.map((msg) => ({
        role: msg.user,
        content: msg.content,
      }));

      console.log("Sending request with context:", {
        message: currentInput,
        message_history: messageHistory,
        itinerary_progress: itineraryProgress,
        session_id: sessionId,
      });

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentInput,
          stream: true,
          message_history: messageHistory,
          itinerary_progress: itineraryProgress,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let fullContent = ""; // Track the full content to avoid duplication

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        // Process each SSE message directly (no buffering needed since Pydantic-AI sends complete messages)
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const jsonStr = line.substring(6); // Remove 'data: ' prefix
              if (jsonStr.trim() === "") continue;

              const data = JSON.parse(jsonStr);

              if (data.error) {
                throw new Error(data.error);
              }

              if (data.content) {
                // Only append new content (avoid duplication from cumulative chunks)
                const newContent = data.content.substring(fullContent.length);
                if (newContent) {
                  fullContent = data.content;

                  setMessages((prev) => {
                    const lastMessage = prev[prev.length - 1];
                    const updatedLastMessage = {
                      ...lastMessage,
                      content: fullContent,
                      isThinking: false,
                    };
                    return [...prev.slice(0, -1), updatedLastMessage];
                  });
                }
              }

              // Handle itinerary progress updates
              if (data.itinerary_progress) {
                console.log(
                  "Updating itinerary progress:",
                  data.itinerary_progress,
                );
                setItineraryProgress(data.itinerary_progress);
              }

              // Log when streaming is done
              if (data.done) {
                console.log("Streaming completed. Final state:", {
                  messagesCount: messages.length + 1,
                  itineraryProgress:
                    data.itinerary_progress || itineraryProgress,
                });
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e, "Raw line:", line);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);

      let errorMessage = "Sorry, I encountered an error. Please try again.";

      // Provide more specific error messages for common issues
      if (error instanceof Error) {
        if (error.message.includes("Failed to fetch")) {
          errorMessage =
            "Unable to connect to the server. Please check if the backend is running.";
        } else if (error.message.includes("HTTP error! status: 500")) {
          errorMessage = "Server error occurred. Please try again in a moment.";
        } else if (error.message.includes("JSON.parse")) {
          errorMessage = "Received invalid data format from server.";
        } else if (error.message.includes("NetworkError")) {
          errorMessage =
            "Network connection lost. Please check your internet connection.";
        }
      }

      setMessages((prev) => {
        const lastMessage = prev[prev.length - 1];
        const updatedLastMessage = {
          ...lastMessage,
          content: errorMessage,
          isThinking: false,
        };
        return [...prev.slice(0, -1), updatedLastMessage];
      });
    }
  };

  return (
    <div className="grid grid-cols-2 h-screen overflow-hidden">
      <ChatUI
        messages={messages}
        input={input}
        setInput={setInput}
        sendMessage={sendMessage}
      />
      <ItineraryDisplay itineraryProgress={itineraryProgress} />
    </div>
  );
}
