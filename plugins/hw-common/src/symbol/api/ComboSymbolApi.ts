import { transceiver } from '../../txrx/Transceiver';
import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';

interface ComboSymbol extends ConfigSymbol<string> {
  options: string[];
}

class ComboSymbolApi extends ConfigSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'ComboSymbol';
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

  getOptions = async (componentId: string, symbolId: string): Promise<string[]> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getOptions',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.options;
  };

  getComboSymbol = async (componentId: string, symbolId: string): Promise<ComboSymbol> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getComboSymbol',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data as ComboSymbol;
  };
}

export const comboSymbolApi = new ComboSymbolApi();

export type { ComboSymbol };

export default ComboSymbolApi;
