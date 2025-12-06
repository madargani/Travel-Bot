export default function ThinkingDots() {
  return (
    <div className="flex space-x-1">
      <div className="w-2 h-2 bg-gray-600 rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></div>
      <div className="w-2 h-2 bg-gray-600 rounded-full animate-pulse" style={{ animationDelay: '150ms' }}></div>
      <div className="w-2 h-2 bg-gray-600 rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></div>
    </div>
  );
}