import { Message } from "../types/Message";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ThinkingDots from "./ThinkingDots";

export default function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="flex-1">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`p-4 max-w-xs rounded-xl my-4 break-words whitespace-pre-wrap ${
            msg.user === "user"
              ? "bg-blue-500 text-white ml-auto"
              : "bg-gray-300 text-black"
          }`}
        >
          {msg.isThinking ? (
            <ThinkingDots />
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.content}
            </ReactMarkdown>
          )}
        </div>
      ))}
    </div>
  );
}
