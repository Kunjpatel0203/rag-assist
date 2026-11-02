import { useState } from "react";

export default function ChatInput({ onSend }) {

  const [text, setText] = useState("");

  const handleSend = () => {

    if(!text.trim()) return;

    onSend(text);
    setText("");
  };

  return (

    <div className="chat-input-container">

      <input
        className="chat-input-field"
        value={text}
        placeholder="Ask anything about your documents..."
        onChange={(e)=>setText(e.target.value)}
        onKeyDown={(e)=>e.key==="Enter" && handleSend()}
      />

      <button
        className="chat-send-btn"
        onClick={handleSend}
      >
        Send
      </button>

    </div>

  );

}