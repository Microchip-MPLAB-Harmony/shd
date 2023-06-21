import { transceiver } from '../../txrx/Transceiver';
import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';

type BooleanSymbol = ConfigSymbol<boolean> & {
  symbolType: 'BooleanSymbol';
};

class BooleanSymbolApi extends ConfigSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'BooleanSymbol';
  }

  getValue = async (componentId: string, symbolId: string): Promise<boolean> => {
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

  setValue = async (componentId: string, symbolId: string, value: boolean): Promise<void> => {
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

  getBooleanSymbol = async (componentId: string, symbolId: string): Promise<BooleanSymbol> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getBooleanSymbol',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data as BooleanSymbol;
  };
}

export const booleanSymbolApi = new BooleanSymbolApi();

export type { BooleanSymbol };

export default BooleanSymbolApi;
