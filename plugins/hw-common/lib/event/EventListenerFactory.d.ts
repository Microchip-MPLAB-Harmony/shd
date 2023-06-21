import { EventFilter, EventListener } from './EventInterfaces';
declare const toSymbolValueListener: (eventConsumer: (e: any) => void, eventFilter?: EventFilter) => EventListener;
declare const toSymbolVisibleListener: (eventConsumer: (e: any) => void, eventFilter?: EventFilter) => EventListener;
declare const toSymbolStateListener: (eventConsumer: (e: any) => void, eventFilter?: EventFilter) => EventListener;
export { toSymbolValueListener, toSymbolVisibleListener, toSymbolStateListener };
