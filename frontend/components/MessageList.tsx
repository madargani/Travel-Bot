import { Message } from "../types/Message";

export default function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="flex-1">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`p-4 max-w-xs ${
            msg.user === "user"
              ? "bg-blue-500 text-white ml-auto"
              : "bg-gray-300 text-black"
          }`}
        >
          {msg.content}
        </div>
      ))}
    </div>
  );
}
