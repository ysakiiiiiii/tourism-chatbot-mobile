import axios from "axios";

const http = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// ============================================================================
// CHAT API
// ============================================================================
export const chatAPI = {
  healthCheck: async () => {
    const response = await http.get("/health");
    return response.data;
  },

  sendMessage: async (message, sessionId = null) => {
    const response = await http.post("/api/chat/", {
      message,
      session_id: sessionId,
    });
    return response.data;
  },

  getHistory: async (sessionId) => {
    const response = await http.get(`/api/chat/history/${sessionId}`);
    return response.data;
  },

  getAllHistory: async (limit = 50) => {
    const response = await http.get("/api/chat/history", {
      params: { limit },
    });
    return response.data;
  },

  deleteHistory: async (sessionId) => {
    const response = await http.delete(`/api/chat/history/${sessionId}`);
    return response.data;
  },

  getContext: async (sessionId) => {
    const response = await http.get(`/api/chat/context/${sessionId}`);
    return response.data;
  },

  resetContext: async (sessionId) => {
    const response = await http.post(`/api/chat/reset/${sessionId}`);
    return response.data;
  },
};

// ============================================================================
// LOCATION & ROUTING API
// ============================================================================
export const locationAPI = {
  /**
   * Get route from current location to destination
   * @param {number} latitude - User's current latitude
   * @param {number} longitude - User's current longitude
   * @param {string} destinationId - Destination ID (e.g., "CU01")
   * @returns {Promise} Route data with steps, fare, time
   */
  getRoute: async (latitude, longitude, destinationId) => {
    const response = await http.post("/api/location/route", {
      latitude,
      longitude,
      destination_id: destinationId,
    });
    return response.data;
  },

  /**
   * Find nearby places within radius
   * @param {number} latitude - User's latitude
   * @param {number} longitude - User's longitude
   * @param {number} radiusKm - Search radius in kilometers (default: 5)
   * @param {number} limit - Max results (default: 10)
   * @returns {Promise} Array of nearby places
   */
  getNearbyPlaces: async (latitude, longitude, radiusKm = 5, limit = 10) => {
    const response = await http.get("/api/location/nearby", {
      params: {
        latitude,
        longitude,
        radius_km: radiusKm,
        limit,
      },
    });
    return response.data;
  },

  /**
   * Get coordinates for a specific location
   * @param {string} locationName - Location name (e.g., "Laoag", "Pagudpud")
   * @returns {Promise} Location coordinates
   */
  getLocationCoordinates: async (locationName) => {
    const response = await http.get(
      `/api/location/coordinates/${encodeURIComponent(locationName)}`
    );
    return response.data;
  },

  /**
   * Get all available transport routes
   * @returns {Promise} Object with jeepney, bus, van, tricycle routes
   */
  getTransportRoutes: async () => {
    const response = await http.get("/api/location/transport-routes");
    return response.data;
  },
};

// ============================================================================
// GEOLOCATION HELPERS
// ============================================================================
export const geolocationHelpers = {
  /**
   * Get user's current location
   * @returns {Promise<{latitude: number, longitude: number, accuracy: number}>}
   */
  getUserLocation: () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("Geolocation is not supported by your browser"));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          });
        },
        (error) => {
          let message = "Unable to get your location";

          switch (error.code) {
            case error.PERMISSION_DENIED:
              message =
                "Location permission denied. Please enable location access in your browser settings.";
              break;
            case error.POSITION_UNAVAILABLE:
              message = "Location information is unavailable.";
              break;
            case error.TIMEOUT:
              message = "Location request timed out.";
              break;
          }

          reject(new Error(message));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    });
  },

  /**
   * Check if geolocation is available
   * @returns {boolean}
   */
  isGeolocationAvailable: () => {
    return "geolocation" in navigator;
  },

  /**
   * Request location permission
   * @returns {Promise<PermissionState>} - 'granted', 'denied', or 'prompt'
   */
  checkLocationPermission: async () => {
    if (!navigator.permissions) {
      return "prompt"; // Assume we need to prompt if API not available
    }

    try {
      const result = await navigator.permissions.query({ name: "geolocation" });
      return result.state; // 'granted', 'denied', or 'prompt'
    } catch (error) {
      console.error("Permission check error:", error);
      return "prompt";
    }
  },
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
export const utils = {
  /**
   * Calculate distance between two points using Haversine formula
   * @param {number} lat1 - First point latitude
   * @param {number} lon1 - First point longitude
   * @param {number} lat2 - Second point latitude
   * @param {number} lon2 - Second point longitude
   * @returns {number} Distance in kilometers
   */
  calculateDistance: (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Earth's radius in km
    const toRad = (deg) => deg * (Math.PI / 180);

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) *
        Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);

    const c = 2 * Math.asin(Math.sqrt(a));
    return R * c;
  },

  /**
   * Format distance for display
   * @param {number} km - Distance in kilometers
   * @returns {string} Formatted distance (e.g., "500m" or "2.5km")
   */
  formatDistance: (km) => {
    if (km < 1) {
      return `${Math.round(km * 1000)}m`;
    }
    return `${km.toFixed(1)}km`;
  },

  /**
   * Format time for display
   * @param {number} minutes - Time in minutes
   * @returns {string} Formatted time (e.g., "30 min" or "1h 30m")
   */
  formatTime: (minutes) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  },

  /**
   * Format fare for display
   * @param {number} amount - Fare amount
   * @returns {string} Formatted fare (e.g., "₱50.00")
   */
  formatFare: (amount) => {
    return `₱${amount.toFixed(2)}`;
  },

  /**
   * Generate a random session ID
   * @returns {string} Session ID
   */
  generateSessionId: () => {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Get or create session ID from localStorage
   * @returns {string} Session ID
   */
  getOrCreateSessionId: () => {
    let sessionId = localStorage.getItem("chat_session_id");
    if (!sessionId) {
      sessionId = utils.generateSessionId();
      localStorage.setItem("chat_session_id", sessionId);
    }
    return sessionId;
  },

  /**
   * Clear session ID from localStorage
   */
  clearSessionId: () => {
    localStorage.removeItem("chat_session_id");
  },
};

// ============================================================================
// ERROR HANDLER
// ============================================================================
http.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      console.error("API Error:", error.response.data);
      throw new Error(error.response.data.detail || "An error occurred");
    } else if (error.request) {
      // Request made but no response
      console.error("Network Error:", error.request);
      throw new Error("Network error. Please check your connection.");
    } else {
      // Something else happened
      console.error("Error:", error.message);
      throw error;
    }
  }
);

// ============================================================================
// COMBINED WORKFLOWS (High-level functions)
// ============================================================================
export const workflows = {
  /**
   * Get route with automatic location detection
   * @param {string} destinationId - Destination ID
   * @returns {Promise} Route data
   */
  getRouteFromCurrentLocation: async (destinationId) => {
    const location = await geolocationHelpers.getUserLocation();
    return locationAPI.getRoute(
      location.latitude,
      location.longitude,
      destinationId
    );
  },

  /**
   * Find nearby places from current location
   * @param {number} radiusKm - Search radius (default: 5km)
   * @param {number} limit - Max results (default: 10)
   * @returns {Promise} Array of nearby places
   */
  getNearbyFromCurrentLocation: async (radiusKm = 5, limit = 10) => {
    const location = await geolocationHelpers.getUserLocation();
    return locationAPI.getNearbyPlaces(
      location.latitude,
      location.longitude,
      radiusKm,
      limit
    );
  },

  /**
   * Send chat message with automatic session management
   * @param {string} message - User message
   * @returns {Promise} Chat response
   */
  sendChatMessage: async (message) => {
    const sessionId = utils.getOrCreateSessionId();
    return chatAPI.sendMessage(message, sessionId);
  },

  /**
   * Reset entire conversation (context + history)
   * @returns {Promise}
   */
  resetConversation: async () => {
    const sessionId = utils.getOrCreateSessionId();
    await chatAPI.resetContext(sessionId);
    await chatAPI.deleteHistory(sessionId);
    utils.clearSessionId();
  },
};

// ============================================================================
// EXPORTS
// ============================================================================
export default http;