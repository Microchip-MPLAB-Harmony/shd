import { transceiver } from '../../txrx/Transceiver';
import ConfigSymbolApi from './ConfigSymbolApi';
import { log } from '@mplab_harmony/harmony-plugin-core-service';
import { IntegerSymbol } from './IntegerSymbolApi';

type FloatSymbol = IntegerSymbol;

class FloatSymbolApi extends ConfigSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'FloatSymbol';
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

  getFloatSymbol = async (componentId: string, symbolId: string): Promise<FloatSymbol> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getFloatSymbol',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data as FloatSymbol;
  };
}

export const floatSymbolApi = new FloatSymbolApi();

export type { FloatSymbol };

export default FloatSymbolApi;
