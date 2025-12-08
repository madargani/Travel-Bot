import { render, screen } from '@testing-library/react';
import ItineraryDisplay from '../components/ItineraryDisplay';
import { ItineraryProgress } from '../types/Message';

// Mock test to verify component renders
describe('ItineraryDisplay', () => {
  it('renders empty state correctly', () => {
    const emptyProgress: ItineraryProgress = { stage: 'initial' };
    render(<ItineraryDisplay itineraryProgress={emptyProgress} />);
    
    expect(screen.getByText('Your Itinerary')).toBeInTheDocument();
    expect(screen.getByText('Start planning to see your trip details here')).toBeInTheDocument();
  });

  it('renders flights information when available', () => {
    const flightProgress: ItineraryProgress = {
      stage: 'flights',
      flights: {
        origin: 'SFO',
        destination: 'JFK',
        departure_date: '2024-12-15',
        return_date: '2024-12-22'
      }
    };
    
    render(<ItineraryDisplay itineraryProgress={flightProgress} />);
    
    expect(screen.getByText('Flights')).toBeInTheDocument();
    expect(screen.getByText('SFO → JFK')).toBeInTheDocument();
    expect(screen.getByText('2024-12-15 - 2024-12-22')).toBeInTheDocument();
  });
});