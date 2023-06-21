import { transceiver } from '../../txrx/Transceiver';
import SymbolApi, { ISymbol } from './SymbolApi';

interface VisibleSymbol extends ISymbol {
  visible: boolean;
}

class VisibleSymbolApi extends SymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'VisibleSymbol';
  }

  getVisible = async (componentId: string, symbolId: string): Promise<boolean> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getVisible',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.visible;
  };
}

export type { VisibleSymbol };

export const visibleSymbolApi = new VisibleSymbolApi();

export default VisibleSymbolApi;
