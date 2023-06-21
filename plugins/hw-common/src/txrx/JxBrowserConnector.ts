// import { v4 as uuidv4 } from 'uuid';
import { Connector, Request, Response, transceiver } from './Transceiver';
import {
  log,
  error,
} from '@mplab_harmony/harmony-plugin-core-service/build/log/CustomConsole';

class JxBrowserConnector implements Connector {
  private readonly _uuid = 'defaultUUID'; //uuidv4();

  constructor() {
    log('ClientJxBrowserConnector : Constructor');
    (window as any).clientJxBrowserConnectorReceive = this.receive;
    // (window as any).receive = this.receive;
  }

  send(request: Request) {
    request.uuid = this._uuid;
    // log('Client JxBrowser Connector : sending Request : ' + JSON.stringify(request));
    (window as any).serverJxBrowserConnector.receive(JSON.stringify(request));
  }

  receive(response: string) {
    // log('Client JxBrowser Connector : receiving response : ' + response);
    try {
      transceiver.receive(JSON.parse(response) as Response);
    } catch (e) {
      error(
        `Client JxBrowser Connector : Parsing Response Failed. ${response}`
      );
    }
  }
}

export const jxBrowserConnector = new JxBrowserConnector();
