import ChatInput from "./ChatInput";
import MessageList from "./MessageList";
import { Message } from "../types/Message";
import { KeyboardEvent } from 'react';

interface ChatUIProps {
  input: string;
  setInput: (value: string) => void;
  messages: Message[];
  sendMessage: (e?: KeyboardEvent<HTMLInputElement>) => void;
}

export default function ChatUI({
  input,
  setInput,
  messages,
  sendMessage,
}: ChatUIProps) {
  return (
    <div className="flex flex-col">
      <MessageList messages={messages} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
}
