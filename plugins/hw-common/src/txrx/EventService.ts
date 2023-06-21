import { EventFilter, EventListener } from '../event/EventInterfaces';
import React from 'react';
import { IEventAgent, Response, transceiver } from './Transceiver';
import { v4 as uuidv4 } from 'uuid';

class EventAgent implements IEventAgent {
  // event name, {componentId, symbolId} as Event Filter, event consumer
  private readonly _eventListeners: Map<
    string,
    Map<string, Set<(e: any) => void>>
  > = new Map();
  private readonly _eventAgentId: string = uuidv4();

  public get id(): string {
    return this._eventAgentId;
  }

  public receive(event: Response) {
    if (!event.eventName) {
      return;
    }
    const filterListenerMap = this._eventListeners.get(event.eventName);
    if (!filterListenerMap) return;

    const { componentId, symbolId } = event.data.symbol || event.data.component;
    filterListenerMap
      .get(this.toHash({}))
      ?.forEach((eventConsumer) => eventConsumer(event));
    componentId &&
      filterListenerMap
        .get(this.toHash({ componentId }))
        ?.forEach((eventConsumer) => eventConsumer(event));
    symbolId &&
      filterListenerMap
        .get(this.toHash({ symbolId }))
        ?.forEach((eventConsumer) => eventConsumer(event));
    if (componentId && symbolId) {
      filterListenerMap
        .get(this.toHash({ componentId, symbolId }))
        ?.forEach((eventConsumer) => eventConsumer(event));
    }
  }

  public addEventListener(eventListener: EventListener) {
    const { eventName } = eventListener;
    let filterListenerMap = this._eventListeners.get(eventName);
    if (!filterListenerMap) {
      filterListenerMap = new Map();
      this._eventListeners.set(eventName, filterListenerMap);
    }

    const eventFilter: EventFilter = eventListener.eventFilter || {};
    let listeners = filterListenerMap.get(this.toHash(eventFilter));

    if (!listeners) {
      listeners = new Set();
      filterListenerMap.set(this.toHash(eventFilter), listeners);
    }

    listeners.add(eventListener.eventConsumer);

    this.registerFilters([{ eventName, ...eventFilter }]);

    // transceiver.send({
    //   path: 'event',
    //   method: 'registerFilters',
    //   data: {
    //     eventFilterCacheId: this._eventAgentId,
    //     filters: [{ eventName, ...eventFilter }]
    //   }
    // });
  }

  // getValue = async (componentId: string, symbolId: string): Promise<boolean> => {
  //   const response = await transceiver.send({
  //     path: this.path,
  //     method: 'getValue',
  //     data: {
  //       componentId,
  //       symbolId
  //     }
  //   });
  //   return response.data.value;
  // };

  registerFilters = async (
    filters: ({ eventName: string } & EventFilter)[]
  ) => {
    const response = await transceiver.send({
      path: 'event',
      method: 'registerFilters',
      data: {
        eventFilterCacheId: this._eventAgentId,
        filters,
      },
    });
    return response.data;
  };

  public removeEventListener(eventListener: EventListener) {
    const { eventName } = eventListener;
    const filterListenerMap = this._eventListeners.get(eventName);

    if (filterListenerMap) {
      const eventFilter: EventFilter = eventListener.eventFilter || {};
      const listeners = filterListenerMap.get(this.toHash(eventFilter));

      const isDeleted = listeners?.delete(eventListener.eventConsumer);

      isDeleted &&
        listeners?.size === 0 &&
        transceiver.send({
          path: 'event',
          method: 'deregisterFilters',
          data: {
            eventFilterCacheId: this._eventAgentId,
            filters: [{ eventName, ...eventFilter }],
          },
        });
    }
  }

  public destroy(): void {
    transceiver.send({
      path: 'event',
      method: 'destroyEventFilterCache',
      data: {
        eventFilterCacheId: this._eventAgentId,
      },
    });
    // this may not be required since this whole event object is garbage collected
    this._eventListeners.clear();
  }

  toHash(eventFilter?: EventFilter) {
    if (!eventFilter) {
      return ':';
    }

    const componentId = eventFilter.componentId || '';
    const symbolId = eventFilter.symbolId || '';

    return `${componentId}:${symbolId}`;
  }

  fromHash(hash: string): EventFilter {
    if (hash === ':') {
      return {};
    }

    const abc = hash.split(':');

    return { componentId: abc[0] || '', symbolId: abc[1] || '' };
  }
}

export const EventAgentContext = React.createContext<EventAgent>(
  new EventAgent()
);

export default EventAgent;
