import { EventFilter, EventListener } from '../event/EventInterfaces';
import React from 'react';
import { IEventAgent, Response } from './Transceiver';
declare class EventAgent implements IEventAgent {
    private readonly _eventListeners;
    private readonly _eventAgentId;
    get id(): string;
    receive(event: Response): void;
    addEventListener(eventListener: EventListener): void;
    registerFilters: (filters: ({
        eventName: string;
    } & EventFilter)[]) => Promise<any>;
    removeEventListener(eventListener: EventListener): void;
    destroy(): void;
    toHash(eventFilter?: EventFilter): string;
    fromHash(hash: string): EventFilter;
}
export declare const EventAgentContext: React.Context<EventAgent>;
export default EventAgent;
