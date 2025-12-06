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

    const newMessage: Message = { user: "user", content: input };
    setMessages([...messages, newMessage]);
    setInput("");

    const responseIndex = messages.length;
    setMessages((prev) => [...prev, { user: "assistant", content: "", isThinking: true }]);

    const response = await fetch(
      `http://localhost:8000/prompt?prompt=${encodeURI(input)}`,
      {
        method: "POST",
        headers: {
          accept: "application/json",
        },
        body: "",
      },
    );

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      console.log(chunk);

      setMessages((prev) => {
        const lastMessage = prev[prev.length - 1];
        const updatedLastMessage = {
          ...lastMessage,
          content: lastMessage.content + chunk,
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
