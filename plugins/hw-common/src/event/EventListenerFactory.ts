import { EventFilter, EventListener } from './EventInterfaces';

const toSymbolValueListener = (eventConsumer: (e: any) => void, eventFilter?: EventFilter) => {
  return {
    eventName: 'SymbolValueChangedEvent',
    eventFilter,
    eventConsumer
  } as EventListener;
};

const toSymbolVisibleListener = (eventConsumer: (e: any) => void, eventFilter?: EventFilter) => {
  return {
    eventName: 'SymbolVisualChangedEvent',
    eventFilter,
    eventConsumer
  } as EventListener;
};

const toSymbolStateListener = (eventConsumer: (e: any) => void, eventFilter?: EventFilter) => {
  return {
    eventName: 'SymbolStateChangedEvent',
    eventFilter,
    eventConsumer
  } as EventListener;
};

export { toSymbolValueListener, toSymbolVisibleListener, toSymbolStateListener };
