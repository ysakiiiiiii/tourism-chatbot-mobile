import { useState, useEffect } from "react";
import { 
  FaTimes, FaWalking, FaBus, FaCar, FaMotorcycle, 
  FaMapMarkerAlt, FaClock, FaMoneyBillWave, FaRoute, FaLocationArrow, FaSpinner, FaInfoCircle
} from "react-icons/fa";

const TRANSPORT_ICONS = {
  walking: FaWalking,
  jeepney: FaBus,
  bus: FaBus,
  tricycle: FaMotorcycle,
  van: FaCar,
};

const TRANSPORT_COLORS = {
  walking: "text-green-600 bg-green-50",
  jeepney: "text-blue-600 bg-blue-50",
  bus: "text-purple-600 bg-purple-50",
  tricycle: "text-orange-600 bg-orange-50",
  van: "text-indigo-600 bg-indigo-50",
};

function TravelDetailsModal({ 
  destinationId, 
  destinationName, 
  destinationLocation, 
  destinationDescription, 
  destinationType,         
  onClose 
}) {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // ========== DEBUG: Log props received ==========

  useEffect(() => {
    fetchRoute();
  }, []);

  const fetchRoute = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get user's current location - Direct browser geolocation
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        });
      });

      const { latitude, longitude, accuracy } = position.coords;
      setUserLocation({ latitude, longitude, accuracy });

      // Fetch route from API - Direct fetch, no wrapper
      const response = await fetch("http://localhost:8000/api/location/route", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          latitude,
          longitude,
          destination_id: destinationId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch route");
      }

      const data = await response.json();
      setRouteData(data);
    } catch (err) {
      console.error("Route fetch error:", err);
      setError(err.message || "Failed to get travel directions");
    } finally {
      setLoading(false);
    }
  };

  const refreshLocation = async () => {
    setRefreshing(true);
    try {
      // Get fresh location
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        });
      });

      const { latitude, longitude, accuracy } = position.coords;
      setUserLocation({ latitude, longitude, accuracy });

      // Recalculate route immediately
      const response = await fetch("http://localhost:8000/api/location/route", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          latitude,
          longitude,
          destination_id: destinationId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch route");
      }

      const data = await response.json();
      setRouteData(data);
    } catch (err) {
      console.error("Refresh error:", err);
      setError(err.message || "Failed to refresh route");
    } finally {
      setRefreshing(false);
    }
  };

  const formatCoords = (lat, lon) => `${lat.toFixed(4)}, ${lon.toFixed(4)}`;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 font-poppins">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-6 flex justify-between items-start">
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-1">{destinationName}</h2>
            <p className="text-purple-100 text-sm flex items-center gap-1">
              <FaMapMarkerAlt className="w-3 h-3" />
              {destinationLocation}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 p-2 rounded-full transition-colors"
          >
            <FaTimes className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mb-4"></div>
              <p className="text-gray-600 font-medium">Calculating best route...</p>
              <p className="text-gray-500 text-sm">Getting your location and finding directions</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-600 font-medium mb-2">⚠️ Error</p>
              <p className="text-red-700 text-sm mb-3">{error}</p>
              <button
                onClick={fetchRoute}
                className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                Try Again
              </button>
            </div>
          )}

          {routeData && userLocation && (
            <div className="space-y-6">
              {/* Description Card - NEW */}
              {destinationDescription && (
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <FaInfoCircle className="text-white text-lg" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        About {destinationType === 'cuisine' ? 'This Dish' : 'This Place'}
                      </h3>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        {destinationDescription}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* User Location Card */}
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-4 text-white shadow-md">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center animate-pulse">
                        <FaLocationArrow className="text-sm" />
                      </div>
                      <p className="font-bold text-sm">📍 YOUR LOCATION</p>
                    </div>
                    <p className="text-sm font-mono text-blue-100 mb-2">
                      {formatCoords(userLocation.latitude, userLocation.longitude)}
                    </p>
                    {userLocation.accuracy && (
                      <p className="text-xs text-blue-200">
                        GPS Accuracy: ±{userLocation.accuracy.toFixed(0)}m
                      </p>
                    )}
                  </div>
                  <button
                    onClick={refreshLocation}
                    disabled={refreshing}
                    className={`px-3 py-2 rounded-lg font-semibold text-xs transition-all ${
                      refreshing
                        ? "bg-white/30 text-white/70 cursor-not-allowed"
                        : "bg-white text-blue-600 hover:bg-blue-50 active:scale-95"
                    }`}
                  >
                    {refreshing ? (
                      <FaSpinner className="animate-spin inline" />
                    ) : (
                      <>
                        <FaLocationArrow className="inline mr-1" />
                        Refresh
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <FaRoute className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-blue-600">
                    {routeData.total_distance_km} km
                  </p>
                  <p className="text-xs text-blue-700">Distance</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <FaClock className="w-6 h-6 text-green-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-green-600">
                    {routeData.total_time_minutes} min
                  </p>
                  <p className="text-xs text-green-700">Duration</p>
                </div>
                <div className="bg-orange-50 rounded-lg p-4 text-center">
                  <FaMoneyBillWave className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-orange-600">
                    ₱{routeData.total_fare}
                  </p>
                  <p className="text-xs text-orange-700">Total Fare</p>
                </div>
              </div>

              {/* Warnings */}
              {routeData.warnings && routeData.warnings.length > 0 && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                  <p className="text-sm text-yellow-800">
                    ⚠️ {routeData.warnings.join(". ")}
                  </p>
                </div>
              )}

              {/* Step-by-step directions */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FaRoute className="text-purple-500" />
                  Step-by-Step Directions
                </h3>

                <div className="space-y-4">
                  {routeData.steps.map((step, index) => {
                    const Icon = TRANSPORT_ICONS[step.transport_mode] || FaWalking;
                    const colorClass = TRANSPORT_COLORS[step.transport_mode] || "text-gray-600 bg-gray-50";
                    const isLastStep = index === routeData.steps.length - 1;

                    return (
                      <div key={step.step_number} className="flex gap-4">
                        {/* Step indicator */}
                        <div className="flex flex-col items-center">
                          <div className={`w-10 h-10 rounded-full ${colorClass} flex items-center justify-center flex-shrink-0`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          {!isLastStep && (
                            <div className="w-0.5 bg-gray-300 flex-1 my-1"></div>
                          )}
                        </div>

                        {/* Step content */}
                        <div className="flex-1 pb-6">
                          <div className="bg-gray-50 rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-semibold text-gray-900">
                                Step {step.step_number}
                              </h4>
                              <span className="text-xs font-medium px-2 py-1 bg-white rounded-full text-gray-600 capitalize">
                                {step.transport_mode}
                              </span>
                            </div>

                            <p className="text-gray-700 mb-3">{step.instruction}</p>

                            <div className="grid grid-cols-2 gap-2 text-sm">
                              {step.distance_km > 0 && (
                                <div className="flex items-center gap-1 text-gray-600">
                                  <FaRoute className="w-3 h-3" />
                                  <span>{step.distance_km} km</span>
                                </div>
                              )}
                              {step.estimated_time_minutes > 0 && (
                                <div className="flex items-center gap-1 text-gray-600">
                                  <FaClock className="w-3 h-3" />
                                  <span>{step.estimated_time_minutes} min</span>
                                </div>
                              )}
                              {step.fare > 0 && (
                                <div className="flex items-center gap-1 text-gray-600">
                                  <FaMoneyBillWave className="w-3 h-3" />
                                  <span>₱{step.fare}</span>
                                </div>
                              )}
                            </div>

                            {step.landmark && (
                              <p className="text-xs text-gray-500 mt-2 italic">
                                💡 {step.landmark}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg font-medium hover:shadow-lg transition-all"
          >
            Got It!
          </button>
        </div>
      </div>
    </div>
  );
}

export default TravelDetailsModal;