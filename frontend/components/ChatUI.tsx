import ChatInput from "./ChatInput";
import MessageList from "./MessageList";
import { Message } from "../types/Message";

export default function ChatUI({
  input,
  setInput,
  messages,
  sendMessage,
}: {
  input: string;
  setInput: (arg0: string) => void;
  messages: Message[];
  sendMessage: (arg0: KeyboardEvent) => void;
}) {
  return (
    <div className="flex flex-col">
      <MessageList messages={messages} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
}
