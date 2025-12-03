import { Message } from "../types/Message";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="flex-1">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`p-4 max-w-xs break-words whitespace-pre-wrap ${
            msg.user === "user"
              ? "bg-blue-500 text-white ml-auto"
              : "bg-gray-300 text-black"
          }`}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {msg.content}
          </ReactMarkdown>
        </div>
      ))}
    </div>
  );
}
