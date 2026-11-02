export default function ChatMessage({ message }) {

  const isUser = message.role === "user";

  return (

    <div className={`message-row ${isUser ? "user-row" : "ai-row"}`}>

      {!isUser && (
        <div className="avatar">
          🤖
        </div>
      )}

      <div className="message-bubble">

        <div className="message-text">
          {message.content}
        </div>

        <div className="message-time">
          {new Date().toLocaleTimeString([], {hour: "2-digit", minute:"2-digit"})}
        </div>

      </div>

      {isUser && (
        <div className="avatar user-avatar">
          🧑
        </div>
      )}

    </div>

  );
}