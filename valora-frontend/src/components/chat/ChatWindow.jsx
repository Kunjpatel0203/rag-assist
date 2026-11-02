import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";

export default function ChatWindow({ messages }) {

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior:"smooth"});
  }, [messages]);

  return (

    <div className="chat-window">

      <div className="chat-messages">

        {messages.map((msg,index)=>(
          <ChatMessage key={msg.id || index} message={msg}/>
        ))}

        <div ref={bottomRef}></div>

      </div>

    </div>

  );
}