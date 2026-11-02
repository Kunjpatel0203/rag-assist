import { useEffect, useState } from "react";
import { getChats, createChat } from "../../services/chatService";

export default function ChatSidebar({ workspaceId, onSelectChat }) {

  const [chats, setChats] = useState([]);

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    const res = await getChats(workspaceId);
    setChats(res.data);
  };

  const handleNewChat = async () => {

    const res = await createChat(workspaceId);

    loadChats();

    onSelectChat(res.data.id);

  };

  return (

    <div className="sidebar">

      <div className="sidebar-header">
        CHATS
      </div>

      <button
        className="new-chat-btn"
        onClick={handleNewChat}
      >
        + New Chat
      </button>

      <div className="chat-list">

        {chats.map(chat => (

          <div
            key={chat.id}
            className="chat-item"
            onClick={() => onSelectChat(chat.id)}
          >

            <div className="chat-dot"></div>

            <div className="chat-info">

              <div className="chat-title">
                {chat.title || "New Chat"}
              </div>

              <div className="chat-sub">
                Ask anything...
              </div>

            </div>

            <div className="chat-time">
              now
            </div>

          </div>

        ))}

      </div>

    </div>

  );

}