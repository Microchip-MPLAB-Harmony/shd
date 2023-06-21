import { Connector, Request } from './Transceiver';
declare class JxBrowserConnector implements Connector {
    private readonly _uuid;
    constructor();
    send(request: Request): void;
    receive(response: string): void;
}
export declare const jxBrowserConnector: JxBrowserConnector;
export {};
