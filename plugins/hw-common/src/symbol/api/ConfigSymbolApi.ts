import { transceiver } from '../../txrx/Transceiver';
import VisibleSymbolApi, { VisibleSymbol } from './VisibleSymbolApi';

interface ConfigSymbol<T> extends VisibleSymbol {
  label: string;
  description: string;
  readOnly: boolean;
  value: T;
}

class ConfigSymbolApi extends VisibleSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'ConfigSymbol';
  }

  getLabel = async (componentId: string, symbolId: string): Promise<string> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getLabel',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.label;
  };

  getDescription = async (componentId: string, symbolId: string): Promise<string> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getDescription',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.description;
  };

  getReadOnly = async (componentId: string, symbolId: string): Promise<boolean> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getReadOnly',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.readOnly;
  };

  getValue = async (componentId: string, symbolId: string): Promise<any> => {
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
}

export const configSymbolApi = new ConfigSymbolApi();

export type { ConfigSymbol };

export default ConfigSymbolApi;
