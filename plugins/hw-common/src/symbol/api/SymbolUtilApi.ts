import { transceiver } from '../../txrx/Transceiver';
import { ISymbol } from './SymbolApi';

class SymbolUtilApi {
  readonly path: string;

  constructor(path?: string) {
    this.path = path || 'SymbolUtil';
  }

  getSymbolTypes = async (componentId: string, symbolIds: string[]): Promise<ISymbol[]> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getSymbolTypes',
      data: {
        componentId,
        symbolIds
      }
    });
    return response.data;
  };

  getSymbols = async (componentId: string, symbolIds: string[]): Promise<any[]> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getSymbols',
      data: {
        componentId,
        symbolIds
      }
    });
    return response.data;
  };

  getChildCount = async (componentId: string, symbolId: string): Promise<number> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getChildCount',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.childCount;
  };

  getChildren = async (componentId: string, symbolId: string): Promise<string[]> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getChildren',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.children;
  };
}

export const symbolUtilApi = new SymbolUtilApi();

export default SymbolUtilApi;
