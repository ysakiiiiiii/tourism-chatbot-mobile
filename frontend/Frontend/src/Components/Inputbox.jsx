import { useState } from 'react';
import { Send, Mic } from 'lucide-react';

function Inputbox({ onSendMessage }) {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) {
      return;
    }

    setIsLoading(true);

    try {
      if (onSendMessage) {
        await onSendMessage(message.trim());
      }
      setMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const handleMicClick = () => {
    setIsListening(!isListening);
    console.log('Microphone toggled:', !isListening);
  };

  return (
    <div className="w-full bg-white p-3 md:p-6 font-poppins">
      <form onSubmit={handleSendMessage} className="flex items-center gap-2 md:gap-3 max-w-3xl mx-auto">
        
        {/* Microphone Button */}
        <button
          type="button"
          onClick={handleMicClick}
          disabled={isLoading}
          className={`flex items-center justify-center p-2 md:p-2.5 rounded-full transition-all duration-300 flex-shrink-0 ${
            isListening
              ? 'bg-red-100 text-red-500'
              : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
          }`}
          title="Voice input"
        >
          <Mic size={18} className="md:w-5 md:h-5" />
        </button>

        {/* Input Field */}
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask for alternatives..."
            disabled={isLoading}
            className="w-full px-4 py-2.5 md:py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-none font-poppins text-sm md:text-base bg-white placeholder-gray-400 text-right transition-all duration-200 hover:border-gray-400"
            dir="rtl"
            style={{
              direction: 'rtl',
              textAlign: 'right',
              unicodeBidi: 'plaintext'
            }}
            rows="1"
          />
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={!message.trim() || isLoading}
          className={`flex items-center justify-center p-2 md:p-2.5 rounded-full transition-all duration-300 flex-shrink-0 font-poppins font-semibold ${
            message.trim() && !isLoading
              ? 'bg-blue-500 text-white hover:bg-blue-600 active:scale-95 cursor-pointer shadow-md hover:shadow-lg'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
          title={isLoading ? 'Sending...' : 'Send message'}
        >
          {isLoading ? (
            <div className="animate-spin">
              <Send size={18} className="md:w-5 md:h-5" />
            </div>
          ) : (
            <Send size={18} className="md:w-5 md:h-5" />
          )}
        </button>
      </form>
    </div>
  );
}

export default Inputbox;