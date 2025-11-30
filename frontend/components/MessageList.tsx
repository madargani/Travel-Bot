export default function MessageList({ messages }) {
  return (
    <div className="flex-1">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`p-4 max-w-xs ${
            msg.sender === "user"
              ? "bg-blue-500 text-white ml-auto"
              : "bg-gray-300 text-black"
          }`}
        >
          {msg.text}
        </div>
      ))}
    </div>
  )
}
