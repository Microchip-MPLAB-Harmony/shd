import { transceiver } from '../../txrx/Transceiver';
import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';

type StringSymbol = ConfigSymbol<string>;

class StringSymbolApi extends ConfigSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'StringSymbol';
  }

  getValue = async (componentId: string, symbolId: string): Promise<string> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getValue',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.value;
  };

  setValue = async (componentId: string, symbolId: string, value: string): Promise<void> => {
    transceiver.send({
      path: this.path,
      method: 'setValue',
      data: {
        componentId,
        symbolId,
        value
      }
    });
    return;
  };

  getStringSymbol = async (componentId: string, symbolId: string): Promise<StringSymbol> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getStringSymbol',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data as StringSymbol;
  };
}

export const stringSymbolApi = new StringSymbolApi();

export type { StringSymbol };

export default stringSymbolApi;
