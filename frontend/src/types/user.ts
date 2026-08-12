export interface User {
  id: string;
  crowdId: string;
  name: string;
  ticketId: string;
  eventId: string;
  currentZoneId: string;
  destinationZoneId?: string;
  gateAssigned?: string;
}
