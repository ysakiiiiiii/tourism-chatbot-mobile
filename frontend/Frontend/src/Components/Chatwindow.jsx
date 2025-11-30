import { useState, useRef, useEffect } from "react";
import Chatbubble from "./Chatbubble";
import Inputbox from "./Inputbox";
import { Menu, Bell, Plus, AlertCircle } from "lucide-react";
import { chatAPI, utils } from "../services/api";

function Chatwindow() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      sender_name: "Bot",
      message:
        "Hello! 👋 Welcome to LocaTour. How can I help you find the perfect tourist destination today?",
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    return utils.getOrCreateSessionId();
  });

  const messagesEndRef = useRef(null);

  useEffect(() => {
    const testConnection = async () => {
      try {
        await chatAPI.healthCheck();
        console.log("Backend connection successful");
        setConnectionError(false);
      } catch (error) {
        console.error("Backend connection failed:", error);
        setConnectionError(true);
      }
    };

    testConnection();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (userMessage) => {
    const userMsg = {
      id: messages.length + 1,
      sender: "human",
      sender_name: "You",
      message: userMessage,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const data = await chatAPI.sendMessage(userMessage, sessionId);

      // Check if there are matched items to display as cards
      const hasMatchedItems =
        data.matched_items && data.matched_items.length > 0;

      const botMsg = {
        id: messages.length + 2,
        sender: "bot",
        sender_name: "Bot",
        message:
          data.response ||
          "Sorry, I couldn't understand that. Please try again.",
        cardData: hasMatchedItems ? data.matched_items[0] : null,
      };

      setMessages((prev) => [...prev, botMsg]);
      setConnectionError(false);
    } catch (error) {
      console.error("Error sending message:", error);

      const errorMsg = {
        id: messages.length + 2,
        sender: "bot",
        sender_name: "Bot",
        message:
          error.message ||
          "Sorry, I encountered an error. Please try again later.",
      };

      setMessages((prev) => [...prev, errorMsg]);
      setConnectionError(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRequestAlternative = (cardData) => {
    handleSendMessage("show me another one");
  };

  const handleNewChat = async () => {
    try {
      await chatAPI.resetContext(sessionId);
      await chatAPI.deleteHistory(sessionId);
      
      utils.clearSessionId();
      const newId = utils.getOrCreateSessionId();
      setSessionId(newId);
      
      setMessages([
        {
          id: 1,
          sender: "bot",
          sender_name: "Bot",
          message:
            "Hello! 👋 Welcome to LocaTour. How can I help you find the perfect tourist destination today?",
        },
      ]);
      
      setConnectionError(false);
    } catch (error) {
      console.error("Error starting new chat:", error);
    }
  };

  return (
    <div className="flex flex-col h-screen max-h-screen w-full">
      {connectionError && (
        <div className="bg-red-50 border-b border-red-200 p-3 flex items-center gap-2 text-sm text-red-800">
          <AlertCircle size={16} />
          <span>
            Cannot connect to server. Make sure the backend is running at
            http://localhost:8000
          </span>
        </div>
      )}

      <div className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="p-3 md:p-4 flex justify-between items-center">
          <div className="flex items-center gap-2 md:gap-3">
            <button
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Open menu"
            >
              <Menu className="text-black" size={20} />
            </button>

            <h1 className="text-base md:text-lg font-extrabold tracking-wide">
              <span className="text-[#ab1cd8] font-poppins">Loca</span>
              <span className="text-[#ff5b6f] font-poppins">Tour</span>
            </h1>
          </div>

          <div className="flex items-center gap-1">
            <button
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors hidden md:flex"
              aria-label="New chat"
              onClick={handleNewChat}
            >
              <Plus className="text-gray-600" size={20} />
            </button>
            <button
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="View notifications"
            >
              <Bell className="text-gray-600" size={20} />
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 md:p-6 space-y-4 bg-gray-50">
        <div className="w-full space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-12">
              <div className="text-center">
                <h2 className="text-2xl md:text-3xl font-extrabold mb-2">
                  <span className="text-[#ab1cd8]">Loca</span>
                  <span className="text-[#ff5b6f]">Tour</span>
                </h2>
                <p className="text-gray-500 text-sm md:text-base">
                  Ask me anything about tourist destinations
                </p>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <Chatbubble
                key={msg.id}
                sender={msg.sender}
                sender_name={msg.sender_name}
                message={msg.message}
                cardData={msg.cardData}
                onRequestAlternative={handleRequestAlternative}
              />
            ))
          )}

          {isLoading && (
            <div className="flex justify-start px-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 md:w-8 md:h-8 bg-gray-200 flex items-center justify-center rounded-full shrink-0">
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                </div>
                <div className="flex items-center gap-2 bg-gray-100 py-3 px-4 rounded-2xl rounded-bl-none">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-gray-200 bg-white">
        <div className="w-full">
          <Inputbox
            onSendMessage={handleSendMessage}
            disabled={connectionError}
          />
        </div>
      </div>
    </div>
  );
}

export default Chatwindow;