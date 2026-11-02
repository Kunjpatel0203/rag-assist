import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

import ChatSidebar from "../components/chat/ChatSidebar";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";
import DocumentPanel from "../components/documents/DocumentPanel";


import { getMessages, askAI } from "../services/messageService";

export default function WorkspacePage() {

  const { workspaceId } = useParams();

  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Load chat history when chat changes
  useEffect(() => {

    if (!chatId) return;

    loadMessages();

  }, [chatId]);

  const loadMessages = async () => {

    const res = await getMessages(chatId);

    setMessages(res.data);

  };

  // Streaming AI response simulation
  const handleSend = async (text) => {

    if (!chatId) {
      alert("Please create or select a chat first");
      return;
    }

    // Add user message instantly
    setMessages(prev => [
      ...prev,
      { role: "user", content: text }
    ]);

    const res = await askAI(chatId, text);

    const answer = res.data.answer;

    let streamed = "";

    for (let i = 0; i < answer.length; i++) {

      streamed += answer[i];

      setMessages(prev => {

        const updated = [...prev];

        const last = updated[updated.length - 1];

        if (last?.role === "assistant") {
          last.content = streamed;
        } else {
          updated.push({
            role: "assistant",
            content: streamed
          });
        }

        return [...updated];
      });

      await new Promise(r => setTimeout(r, 10));
    }
  };

  return (

    <div className="workspace-app">

      {/* TOP BAR */}

      <div className="workspace-topbar">

        <div className="logo">
          🔒 Valora
        </div>

        <div className="workspace-title">

          <select
            className="workspace-switch"
            onChange={(e)=>window.location=`/workspace/${e.target.value}`}
          >

            <option value={workspaceId}>
              Workspace {workspaceId}
            </option>

          </select>

        </div>

        <div className="workspace-actions">
          <button className="settings-btn">
            Settings
          </button>
        </div>

      </div>


      {/* MAIN BODY */}

      <div className="workspace-body">

        {/* SIDEBAR */}

        {sidebarOpen && (

          <div className="chat-sidebar">

            <ChatSidebar
              workspaceId={workspaceId}
              onSelectChat={setChatId}
            />

          </div>

        )}


        {/* CHAT AREA */}

        <div className="chat-center">

          <div className="chat-header">

            <button
              className="sidebar-toggle"
              onClick={()=>setSidebarOpen(!sidebarOpen)}
            >
              ☰
            </button>

            AI Assistant

          </div>

          <ChatWindow messages={messages} />

          <ChatInput onSend={handleSend}/>

        </div>


        {/* DOCUMENT PANEL */}

        <div className="document-panel">

          <DocumentPanel workspaceId={workspaceId}/>

        </div>

      </div>

    </div>

  );

}