import { transceiver } from '../../txrx/Transceiver';
import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';
import { log } from '@mplab_harmony/harmony-plugin-core-service';

interface IntegerSymbol extends ConfigSymbol<number> {
  value: number;
  min: number;
  max: number;
}

class IntegerSymbolApi extends ConfigSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'IntegerSymbol';
  }

  getValue = async (componentId: string, symbolId: string): Promise<number> => {
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

  setValue = async (componentId: string, symbolId: string, value: number): Promise<void> => {
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

  getIntegerSymbol = async (componentId: string, symbolId: string): Promise<IntegerSymbol> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getIntegerSymbol',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data as IntegerSymbol;
  };
}

export const integerSymbolApi = new IntegerSymbolApi();

export type { IntegerSymbol };

export default IntegerSymbolApi;
