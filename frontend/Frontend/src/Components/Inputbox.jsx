import { useState, forwardRef, useEffect, useRef } from 'react';
import { Send, Mic } from 'lucide-react';

const Inputbox = forwardRef(({ onSendMessage, disabled }, ref) => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef(null);

  // Keys to ignore for auto-focus
  const ignoredKeys = new Set([
    "Shift", "Control", "Alt", "Meta",
    "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
    "CapsLock", "Tab", "Escape", "Enter"
  ]);

  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      // Don't auto-focus if disabled
      if (disabled) return;

      // Don't auto-focus if already focused
      if (document.activeElement === textareaRef.current) return;

      // Don't auto-focus if user is typing in another input
      if (document.activeElement?.tagName === 'INPUT' || 
          document.activeElement?.tagName === 'TEXTAREA') return;

      // Don't auto-focus for ignored keys
      if (ignoredKeys.has(e.key)) return;

      // Don't auto-focus if any modifier key is pressed
      if (e.ctrlKey || e.metaKey || e.altKey) return;

      // Focus the textarea for printable characters
      if (e.key.length === 1) {
        textareaRef.current?.focus();
      }
    };

    // Add event listener to document
    document.addEventListener('keydown', handleGlobalKeyDown);

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleGlobalKeyDown);
    };
  }, [disabled]);

  const handleSendMessage = async () => {
    if (!message.trim() || disabled) return;

    setIsLoading(true);
    try {
      if (onSendMessage) await onSendMessage(message.trim());
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
      handleSendMessage();
    }
  };

  const handleMicClick = () => {
    setIsListening(!isListening);
    console.log('Microphone toggled:', !isListening);
  };

  return (
    <div className="w-full bg-white p-3 md:p-6 font-poppins">
      <div className="flex items-center gap-2 md:gap-3 max-w-3xl mx-auto">
        {/* Microphone Button */}
        <button
          type="button"
          onClick={handleMicClick}
          disabled={isLoading || disabled}
          className={`flex items-center justify-center p-2 md:p-2.5 rounded-full transition-all duration-300 shrink-0 ${
            isListening
              ? 'bg-red-100 text-red-500'
              : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
          } ${(isLoading || disabled) ? 'opacity-50 cursor-not-allowed' : ''}`}
          title="Voice input"
        >
          <Mic size={18} className="md:w-5 md:h-5" />
        </button>

        {/* Input Field */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="...Describe what you want to find"
            disabled={isLoading || disabled}
            className="w-full px-4 py-2.5 md:py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-none font-poppins text-sm md:text-base bg-white placeholder-gray-400 text-right transition-all duration-200 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            dir="rtl"
            style={{
              direction: 'rtl',
              textAlign: 'left',
              unicodeBidi: 'plaintext'
            }}
            rows="1"
          />
        </div>

        {/* Send Button */}
        <button
          type="button"
          onClick={handleSendMessage}
          disabled={!message.trim() || isLoading || disabled}
          className={`flex items-center justify-center p-2 md:p-2.5 rounded-full transition-all duration-300 shrink-0 font-poppins font-semibold ${
            message.trim() && !isLoading && !disabled
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
      </div>
    </div>
  );
});

Inputbox.displayName = 'Inputbox';

export default Inputbox;