import { FaRobot } from "react-icons/fa6";
import { FaUser } from "react-icons/fa";

function Chatbubble({ sender_name, sender, message }) {
  return (
    <div className={`font-poppins flex ${sender === "human" ? "justify-end" : "justify-start"} w-full h-auto`}>
      <div className="flex flex-col max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg">
        
        {/* Bubble Name */}
        <div className={`flex w-full h-auto text-xs text-gray-500 mb-1 px-2 ${
          sender === "human" ? "justify-end" : "justify-start"
        }`}>
          <p className="font-medium">{sender === "human" ? sender_name : "LocaTour"}</p>
        </div>

        {/* Wrapper */}
        <div className={`flex ${sender === "human" ? "flex-row-reverse" : "flex-row"} items-end gap-2 px-2`}>
          
          {/* Avatar */}
          <div className="w-7 h-7 md:w-8 md:h-8 bg-gray-200 flex items-center justify-center rounded-full flex-shrink-0">
            {sender === "human" ? (
              <FaUser className="size-3.5 md:size-4 text-gray-600" />
            ) : (
              <FaRobot className="size-3.5 md:size-4 text-gray-600" />
            )}
          </div>

          {/* Message Bubble */}
          <div
            className={`py-2.5 px-3 md:py-3 md:px-4 rounded-2xl text-sm md:text-base break-words ${
              sender === "human"
                ? "bg-blue-500 text-white rounded-br-none"
                : "bg-gray-100 text-gray-800 rounded-bl-none"
            }`}
          >
            <p className="leading-relaxed">{message}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chatbubble;