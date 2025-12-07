import { KeyboardEvent } from 'react';

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  sendMessage: (e?: KeyboardEvent<HTMLInputElement>) => void;
}

export default function ChatInput({ input, setInput, sendMessage }: ChatInputProps) {
  return (
    <div className="flex items-stretch">
      <input
        className="flex-1 border border-gray-300 p-4"
        placeholder="Tell me about your ideal trip..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage(e)}
      />
      <button
        className="bg-blue-500 text-white px-4 py-4"
        onClick={() => sendMessage()}
      >
        Send
      </button>
    </div>
  );
}
