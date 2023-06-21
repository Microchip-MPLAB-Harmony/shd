import { Event } from './Event';

interface SymbolValueChangedEvent extends Event {
  name: string;
  value: any;
}

export type { SymbolValueChangedEvent };
