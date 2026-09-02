import { render, screen } from '@testing-library/react';
import App from './App';

test('renders WSN Energy-Harvesting Routing Simulator title', () => {
  render(<App />);
  const titleElement = screen.getByText(/WSN Energy-Harvesting Routing Simulator/i);
  expect(titleElement).toBeInTheDocument();
});

