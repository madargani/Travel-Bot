export type UserRole = "assistant" | "user";

export type ItineraryProgress = {
  stage: 'initial' | 'flights' | 'hotels' | 'activities' | 'complete';
  flights?: {
    origin?: string;
    destination?: string;
    departure_date?: string;
    return_date?: string;
    selected_option?: any;
  };
  hotels?: {
    city?: string;
    checkin_date?: string;
    checkout_date?: string;
    adults?: number;
    rooms?: number;
    selected_option?: any;
  };
  activities?: {
    city?: string;
    restaurants?: any[];
    events?: any[];
    attractions?: any[];
  };
};

export type Message = {
  user: UserRole;
  content: string;
  isThinking?: boolean;
  itineraryProgress?: ItineraryProgress;
};

// API request/response types
export interface ChatRequest {
  message: string;
  stream: boolean;
  message_history: Array<{role: string, content: string}>;
  itinerary_progress: ItineraryProgress;
  session_id: string;
}

export interface StreamingResponse {
  content?: string;
  done?: boolean;
  itinerary_progress?: ItineraryProgress;
  error?: string;
}
