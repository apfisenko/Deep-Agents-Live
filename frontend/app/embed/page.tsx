import { ChatPage } from "@/components/chat/chat-page";

export default function EmbedPage() {
  return (
    <main className="aira-page-bg flex h-screen items-center justify-center overflow-hidden p-2">
      <ChatPage compact showTelegramLink={false} />
    </main>
  );
}
