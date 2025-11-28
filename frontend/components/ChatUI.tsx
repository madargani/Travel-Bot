"use client";

import { useState } from "react";

import ChatInput from './ChatInput';
import MessageList from './MessageList';

export default function ChatUI() {
  const [messages, setMessages] = useState([
    { sender: "assistant", text: "Hello! How can I help you?"}
  ]);
  const [input, setInput] = useState("");

  const sendMessage = (event) => {
    event.preventDefault();
    if (!input.trim()) return;
    const newMessage = { sender: "user", text: input };
    setMessages([...messages, newMessage]);
    setInput("");
  }

  return (
    <div className="flex flex-col">
      <MessageList messages={messages} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
}
