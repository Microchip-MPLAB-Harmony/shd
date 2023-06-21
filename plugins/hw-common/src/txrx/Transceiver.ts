import { log, error } from '@mplab_harmony/harmony-plugin-core-service';
import { jxBrowserConnector } from './JxBrowserConnector';

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

interface PromiseHolder {
  resolve: (value: ResponseEntity) => void;
  reject: (value: ResponseEntity) => void;
}

class Transceiver {
  private readonly _sequencePromiseMap = new Map<number, PromiseHolder>();
  private requestCounter = 1;
  private readonly _eventAgents = new Map<string, IEventAgent>();

  constructor() {
    log('Client Transceiver : Constructor');
  }

  send(request: RequestEntity): Promise<ResponseEntity> {
    request.sequenceNumber = this.requestCounter++;
    const promise = new Promise<ResponseEntity>((resolve, reject) => {
      const promiseHolder = {
        resolve,
        reject
      };
      request.sequenceNumber && this._sequencePromiseMap.set(request.sequenceNumber, promiseHolder);
    });

    jxBrowserConnector.send(request);
    return promise;
  }

  receive(response: ResponseEntity): void {
    const { status, sequenceNumber, eventName, eventFilterCacheId } = response;
    // log('Client Response Received : ' + JSON.stringify(response));
    if (status === 'event') {
      if (!eventFilterCacheId || !eventName) {
        error(
          'Invalid Event : Event Filter Cache Id or Event Name is empty. Response: ' +
            JSON.stringify(response)
        );
      } else {
        this._eventAgents.get(eventFilterCacheId)?.receive(response);
      }
    } else if (sequenceNumber && this._sequencePromiseMap.has(sequenceNumber)) {
      const promiseHolder = this._sequencePromiseMap.get(sequenceNumber);
      this._sequencePromiseMap.delete(sequenceNumber);
      this.verifyAndResetSequenceNumber();
      if (status === 'success') {
        promiseHolder && promiseHolder.resolve(response);
      } else if (status === 'error') {
        promiseHolder && promiseHolder.reject(response);
      }
    }
  }

  private verifyAndResetSequenceNumber() {
    if (this._sequencePromiseMap.size === 0) {
      if (this.requestCounter > 1000000000000000) {
        this.requestCounter = 1;
      }
    }
  }

  registerEventAgent(eventAgent: IEventAgent): void {
    this._eventAgents.set(eventAgent.id, eventAgent);
  }

  deregisterEventAgent(eventAgent: IEventAgent): boolean {
    return this._eventAgents.delete(eventAgent.id);
  }
}

export const transceiver = new Transceiver();

export type { RequestEntity as Request, ResponseEntity as Response, Connector, IEventAgent };
