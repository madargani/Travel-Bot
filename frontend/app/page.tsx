import ChatUI from '../components/ChatUI';

export default function Page() {
  return (
    <div className="grid grid-cols-2 h-screen">
      <ChatUI />
      <div className="bg-blue-500"></div>
    </div>
  );
}
