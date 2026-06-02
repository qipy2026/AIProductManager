import ChatPanel from "@/components/ChatPanel";

export default function ChatPage({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  return (
    <div>
      <h1>智能客服对话</h1>
      <ChatPanel initialQuery={searchParams.q} />
    </div>
  );
}
