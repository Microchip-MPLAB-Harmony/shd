interface RequestEntity {
    uuid?: string;
    sequenceNumber?: number;
    path: string;
    method: string;
    data: any;
}
interface ResponseEntity {
    status: 'success' | 'error' | 'event';
    uuid?: string;
    sequenceNumber?: number;
    eventName?: string;
    eventFilterCacheId?: string;
    data: any;
}
interface IEventAgent {
    receive(response: ResponseEntity): void;
    readonly id: string;
}
interface Connector {
    send(request: RequestEntity): void;
}
declare class Transceiver {
    private readonly _sequencePromiseMap;
    private requestCounter;
    private readonly _eventAgents;
    constructor();
    send(request: RequestEntity): Promise<ResponseEntity>;
    receive(response: ResponseEntity): void;
    private verifyAndResetSequenceNumber;
    registerEventAgent(eventAgent: IEventAgent): void;
    deregisterEventAgent(eventAgent: IEventAgent): boolean;
}
export declare const transceiver: Transceiver;
export type { RequestEntity as Request, ResponseEntity as Response, Connector, IEventAgent };
