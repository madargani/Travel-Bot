import { ItineraryProgress } from "../types/Message";

interface ItineraryDisplayProps {
  itineraryProgress: ItineraryProgress;
}

export default function ItineraryDisplay({ itineraryProgress }: ItineraryDisplayProps) {
  const getStageLabel = (stage: string) => {
    switch (stage) {
      case 'initial':
        return 'Getting Started';
      case 'flights':
        return 'Planning Flights';
      case 'hotels':
        return 'Choosing Hotels';
      case 'activities':
        return 'Selecting Activities';
      case 'complete':
        return 'Itinerary Complete';
      default:
        return 'Planning';
    }
  };

  const getStageProgress = (stage: string) => {
    const stages = ['initial', 'flights', 'hotels', 'activities', 'complete'];
    const currentIndex = stages.indexOf(stage);
    return stages.map((_, index) => index <= currentIndex);
  };

  // Empty state
  if (itineraryProgress.stage === 'initial' && !itineraryProgress.flights && !itineraryProgress.hotels && !itineraryProgress.activities) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 p-8">
        <div className="text-6xl mb-4">✈️</div>
        <h3 className="text-xl font-semibold text-gray-700">Your Itinerary</h3>
        <p className="text-sm mt-2 text-center text-gray-500">
          Start planning to see your trip details here
        </p>
      </div>
    );
  }

  return (
    <div className="h-full p-6 bg-gray-50 overflow-y-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-3">Trip Itinerary</h2>
        
        {/* Stage Indicator */}
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-sm font-medium text-gray-600">
            {getStageLabel(itineraryProgress.stage)}
          </span>
          <div className="flex space-x-1">
            {getStageProgress(itineraryProgress.stage).map((filled, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  filled ? 'bg-blue-500' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Flights Card */}
      {itineraryProgress.flights && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 shadow-sm">
          <div className="flex items-center mb-3">
            <div className="text-blue-500 mr-2">✈️</div>
            <h4 className="font-semibold text-gray-800">Flights</h4>
          </div>
          <div className="text-sm text-gray-600 space-y-1">
            <div>
              <span className="font-medium">Route:</span> {itineraryProgress.flights.origin} → {itineraryProgress.flights.destination}
            </div>
            <div>
              <span className="font-medium">Dates:</span> {itineraryProgress.flights.departure_date}
              {itineraryProgress.flights.return_date && ` - ${itineraryProgress.flights.return_date}`}
            </div>
            {itineraryProgress.flights.selected_option && (
              <div>
                <span className="font-medium">Selected:</span> Flight option chosen
              </div>
            )}
          </div>
        </div>
      )}

      {/* Hotels Card */}
      {itineraryProgress.hotels && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 shadow-sm">
          <div className="flex items-center mb-3">
            <div className="text-blue-500 mr-2">🏨</div>
            <h4 className="font-semibold text-gray-800">Hotels</h4>
          </div>
          <div className="text-sm text-gray-600 space-y-1">
            <div>
              <span className="font-medium">Location:</span> {itineraryProgress.hotels.city}
            </div>
            <div>
              <span className="font-medium">Dates:</span> {itineraryProgress.hotels.checkin_date} - {itineraryProgress.hotels.checkout_date}
            </div>
            {itineraryProgress.hotels.adults && (
              <div>
                <span className="font-medium">Guests:</span> {itineraryProgress.hotels.adults} adults
                {itineraryProgress.hotels.rooms && ` in ${itineraryProgress.hotels.rooms} room${itineraryProgress.hotels.rooms > 1 ? 's' : ''}`}
              </div>
            )}
            {itineraryProgress.hotels.selected_option && (
              <div>
                <span className="font-medium">Selected:</span> Hotel option chosen
              </div>
            )}
          </div>
        </div>
      )}

      {/* Activities Card */}
      {itineraryProgress.activities && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 shadow-sm">
          <div className="flex items-center mb-3">
            <div className="text-blue-500 mr-2">🎯</div>
            <h4 className="font-semibold text-gray-800">Activities</h4>
          </div>
          <div className="text-sm text-gray-600 space-y-1">
            <div>
              <span className="font-medium">Location:</span> {itineraryProgress.activities.city}
            </div>
            {itineraryProgress.activities.restaurants && itineraryProgress.activities.restaurants.length > 0 && (
              <div>
                <span className="font-medium">Restaurants:</span> {itineraryProgress.activities.restaurants.length} options found
              </div>
            )}
            {itineraryProgress.activities.events && itineraryProgress.activities.events.length > 0 && (
              <div>
                <span className="font-medium">Events:</span> {itineraryProgress.activities.events.length} events available
              </div>
            )}
            {itineraryProgress.activities.attractions && itineraryProgress.activities.attractions.length > 0 && (
              <div>
                <span className="font-medium">Attractions:</span> {itineraryProgress.activities.attractions.length} attractions suggested
              </div>
            )}
          </div>
        </div>
      )}

      {/* Complete State Summary */}
      {itineraryProgress.stage === 'complete' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div className="flex items-center mb-2">
            <div className="text-green-600 mr-2">✅</div>
            <h4 className="font-semibold text-green-800">Itinerary Complete!</h4>
          </div>
          <p className="text-sm text-green-700">
            Your trip is fully planned. You're ready to go!
          </p>
        </div>
      )}
    </div>
  );
}