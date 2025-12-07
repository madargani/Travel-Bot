"use client";

import ChatUI from "../components/ChatUI";
import { useState } from "react";

import { Message } from "../types/Message";

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([
    { user: "assistant", content: "Hello! How can I help you?" },
  ]);
  const [input, setInput] = useState<string>("");

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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentInput,
          stream: true,
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
        console.log("Raw chunk received:", chunk);

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
    <div className="grid grid-cols-2 h-screen">
      <ChatUI
        messages={messages}
        input={input}
        setInput={setInput}
        sendMessage={sendMessage}
      />
      <div className="bg-blue-500"></div>
    </div>
  );
}
