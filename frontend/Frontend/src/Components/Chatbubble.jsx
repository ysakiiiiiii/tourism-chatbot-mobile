import { useState } from "react";
import {
  FaRobot,
  FaUser,
  FaMapMarkerAlt,
  FaClock,
  FaRoute,
  FaExchangeAlt,
} from "react-icons/fa";
import TravelDetailsModal from "./TravelDetailsModal";
import { geolocationHelpers } from "../services/api";

function Chatbubble({
  sender_name,
  sender,
  message,
  cardData,
  onRequestAlternative,
}) {
  const [showTravelModal, setShowTravelModal] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Handler for "Travel Details" button
  const handleTravelDetails = async () => {
    // ========== DEBUG: Log all cardData ==========
    console.log("=== TRAVEL DETAILS DEBUG ===");
    console.log("Full cardData:", cardData);
    console.log("Description:", cardData?.full_description);
    console.log("Type:", cardData?.type);
    console.log("Has description:", !!cardData?.full_description);
    console.log("===========================");

    try {
      if (!geolocationHelpers.isGeolocationAvailable()) {
        alert("Geolocation is not supported by your browser");
        return;
      }

      const permission = await geolocationHelpers.checkLocationPermission();
      if (permission === "denied") {
        alert("Location access denied. Please enable it in browser settings.");
        return;
      }

      setShowTravelModal(true);
    } catch (error) {
      alert(error.message);
    }
  };

  // Handler for "Alternatives" button
  const handleAlternatives = () => {
    if (onRequestAlternative) {
      onRequestAlternative(cardData);
    }
  };

  // Handler for image load error
  const handleImageError = () => {
    setImageError(true);
  };

  // Determine if we should show the actual image or placeholder
  const hasPhoto = cardData?.photo_url && !imageError;

  // If this is a card with place info, render the card
  if (cardData && sender === "bot") {
    return (
      <>
        <div className="font-poppins flex justify-start w-full h-auto">
          <div className="flex flex-col w-full sm:max-w-sm md:max-w-md lg:max-w-lg">
            {/* Bubble Name */}
            <div className="flex w-full h-auto text-xs text-gray-500 mb-1 px-2">
              <p className="font-medium">LocaTour</p>
            </div>

            <div className="flex flex-row items-start gap-2 px-2">
              {/* Avatar */}
              <div className="w-7 h-7 md:w-8 md:h-8 bg-gray-200 flex items-center justify-center rounded-full shrink-0 mt-1">
                <FaRobot className="size-3.5 md:size-4 text-gray-600" />
              </div>

              <div className="flex flex-col gap-3 flex-1 min-w-0">
                {/* Text Message */}
                {message && (
                  <div className="py-2.5 px-3 md:py-3 md:px-4 rounded-2xl rounded-bl-none text-sm md:text-base bg-gray-100 text-gray-800">
                    <p className="leading-relaxed">{message}</p>
                  </div>
                )}

                {/* Tourist Spot Card */}
                <div className="bg-white rounded-xl md:rounded-2xl shadow-lg overflow-hidden border border-gray-200 w-full">
                  {/* Image or Placeholder */}
                  <div className="relative w-full h-40 sm:h-44 md:h-48 overflow-hidden">
                    {hasPhoto ? (
                      // Actual Photo
                      <img
                        src={`/${cardData.photo_url}`}
                        alt={cardData.name}
                        className="w-full h-full object-cover"
                        onError={handleImageError}
                      />
                    ) : (
                      // Placeholder
                      <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 via-blue-400 to-blue-500">
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="text-white/90 text-center px-4">
                            <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-2 sm:mb-3 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                              <FaMapMarkerAlt className="text-2xl sm:text-3xl" />
                            </div>
                            <p className="text-xs sm:text-sm font-semibold tracking-wide">
                              Image Coming Soon
                            </p>
                          </div>
                        </div>
                        <div className="absolute top-4 right-4 w-12 h-12 sm:w-16 sm:h-16 bg-white/10 rounded-full blur-2xl"></div>
                        <div className="absolute bottom-4 left-4 w-16 h-16 sm:w-20 sm:h-20 bg-white/10 rounded-full blur-2xl"></div>
                      </div>
                    )}
                  </div>

                  {/* Card Content */}
                  <div className="p-4 sm:p-5">
                    {/* Title */}
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3 line-clamp-2">
                      {cardData.name}
                    </h3>

                    {/* Location */}
                    <div className="flex items-start gap-2 text-gray-600 mb-2">
                      <FaMapMarkerAlt className="w-4 h-4 shrink-0 mt-0.5" />
                      <p className="text-sm flex-1 line-clamp-2">
                        {cardData.location}
                      </p>
                    </div>

                    {/* Best Time */}
                    <div className="flex items-start gap-2 text-gray-600 mb-4">
                      <FaClock className="w-4 h-4 shrink-0 mt-0.5" />
                      <p className="text-sm flex-1">
                        {cardData.best_time_to_visit || "Anytime"}
                      </p>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-2">
                      {/* Travel Details Button */}
                      <button
                        onClick={handleTravelDetails}
                        disabled={!cardData.has_routing}
                        className={`w-full sm:flex-1 py-2.5 px-4 rounded-full font-medium text-sm transition-all duration-200 flex items-center justify-center gap-2 ${
                          cardData.has_routing
                            ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:scale-105 active:scale-95"
                            : "bg-gray-300 text-gray-500 cursor-not-allowed"
                        }`}
                      >
                        <FaRoute className="w-3.5 h-3.5" />
                        Travel Details
                      </button>

                      {/* Alternatives Button */}
                      <button
                        onClick={handleAlternatives}
                        className="w-full sm:flex-1 border-2 border-gray-300 text-gray-700 py-2.5 px-4 rounded-full font-medium text-sm hover:bg-gray-50 transition-all duration-200 active:scale-95 flex items-center justify-center gap-2"
                      >
                        <FaExchangeAlt className="w-3.5 h-3.5" />
                        Alternatives
                      </button>
                    </div>

                    {/* Show message if routing not available */}
                    {!cardData.has_routing && (
                      <p className="text-xs text-gray-500 mt-2 text-center">
                        Travel directions not available for this location yet
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Travel Modal */}
        {/* Travel Modal */}
        {showTravelModal && (
          <TravelDetailsModal
            destinationId={cardData.destination_id}
            destinationName={cardData.name}
            destinationLocation={cardData.location}
            destinationDescription={cardData.full_description} 
            destinationType={cardData.type} 
            onClose={() => setShowTravelModal(false)}
          />
        )}
      </>
    );
  }

  // Regular text bubble
  return (
    <div
      className={`font-poppins flex ${
        sender === "human" ? "justify-end" : "justify-start"
      } w-full h-auto`}
    >
      <div className="flex flex-col w-full sm:max-w-xs md:max-w-md lg:max-w-lg">
        <div
          className={`flex w-full h-auto text-xs text-gray-500 mb-1 px-2 ${
            sender === "human" ? "justify-end" : "justify-start"
          }`}
        >
          <p className="font-medium">
            {sender === "human" ? sender_name : "LocaTour"}
          </p>
        </div>

        <div
          className={`flex ${
            sender === "human" ? "flex-row-reverse" : "flex-row"
          } items-end gap-2 px-2`}
        >
          <div className="w-7 h-7 md:w-8 md:h-8 bg-gray-200 flex items-center justify-center rounded-full shrink-0">
            {sender === "human" ? (
              <FaUser className="size-3.5 md:size-4 text-gray-600" />
            ) : (
              <FaRobot className="size-3.5 md:size-4 text-gray-600" />
            )}
          </div>

          <div
            className={`py-2.5 px-3 md:py-3 md:px-4 rounded-2xl text-sm md:text-base break-words max-w-[85%] sm:max-w-full ${
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
