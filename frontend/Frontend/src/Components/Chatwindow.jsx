import { useState, useRef, useEffect } from 'react';
import Chatbubble from "./Chatbubble";
import Inputbox from "./Inputbox";
import { Menu, Bell, Plus } from 'lucide-react';

function Chatwindow() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      sender_name: 'Bot',
      message: 'Hello! 👋 Welcome to LocaTour. How can I help you find the perfect tourist destination today?'
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (userMessage) => {
    const userMsg = {
      id: messages.length + 1,
      sender: 'human',
      sender_name: 'You',
      message: userMessage
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Simulate API call to chatbot backend
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          userId: 'user123',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from chatbot');
      }

      const data = await response.json();

      const botMsg = {
        id: messages.length + 2,
        sender: 'bot',
        sender_name: 'Bot',
        message: data.reply || 'Sorry, I couldn\'t understand that. Please try again.'
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMsg = {
        id: messages.length + 2,
        sender: 'bot',
        sender_name: 'Bot',
        message: 'Sorry, I encountered an error. Please try again later.'
      };

      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen md:h-auto md:max-h-[400px]">
      
      {/* Header - ChatGPT Style */}
      <div className='border-b border-gray-200 bg-white sticky top-0 z-10'>
        <div className='p-3 md:p-4 flex justify-between items-center'>
          {/* Left Section */}
          <div className='flex items-center gap-2 md:gap-3'>
            <button 
              className='p-2 hover:bg-gray-100 rounded-lg transition-colors md:hidden'
              aria-label="Open menu"
            >
              <Menu className='text-black' size={20} />
            </button>
            
            <h1 className='text-base md:text-lg font-extrabold tracking-wide'>
              <span className='text-[#ab1cd8]'>Loca</span>
              <span className='text-[#ff5b6f]'>Tour</span>
            </h1>
          </div>

          {/* Right Section */}
          <div className='flex items-center gap-1'>
            <button 
              className='p-2 hover:bg-gray-100 rounded-lg transition-colors hidden md:flex'
              aria-label="New chat"
            >
              <Plus className='text-gray-600' size={20} />
            </button>
            <button 
              className='p-2 hover:bg-gray-100 rounded-lg transition-colors'
              aria-label="View notifications"
            >
              <Bell className='text-gray-600' size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-3 md:p-6 space-y-4">
        <div className="max-w-3xl mx-auto w-full space-y-4">
          {messages.length === 0 ? (
            // Empty State
            <div className="flex flex-col items-center justify-center h-full py-12">
              <div className="text-center">
                <h2 className='text-2xl md:text-3xl font-extrabold mb-2'>
                  <span className='text-[#ab1cd8]'>Loca</span>
                  <span className='text-[#ff5b6f]'>Tour</span>
                </h2>
                <p className='text-gray-500 text-sm md:text-base'>Ask me anything about tourist destinations</p>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <Chatbubble
                key={msg.id}
                sender={msg.sender}
                sender_name={msg.sender_name}
                message={msg.message}
              />
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 bg-gray-100 py-3 px-4 rounded-2xl rounded-bl-none">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Box */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-3xl mx-auto w-full">
          <Inputbox onSendMessage={handleSendMessage} />
        </div>
      </div>
    </div>
  );
}

export default Chatwindow;