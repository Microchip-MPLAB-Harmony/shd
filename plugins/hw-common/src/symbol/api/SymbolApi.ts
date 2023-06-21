import { transceiver } from '../../txrx/Transceiver';

interface SymbolProps {
  componentId: string;
  symbolId: string;
}

interface ISymbol {
  componentId: string;
  symbolId: string;
  symbolType: string;
}

class SymbolApi {
  readonly path: string;

  constructor(path?: string) {
    this.path = path || 'Symbol';
  }

  getSymbolType = async (componentId: string, symbolId: string): Promise<string> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getSymbolType',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.symbolType;
  };

  // getSymbolTypes = async (componentId: string, symbolIds: string[]): Promise<string[]> => {
  //   const response = await transceiver.send({
  //     path: this.path,
  //     method: 'getSymbolTypes',
  //     data: {
  //       componentId,
  //       symbolIds
  //     }
  //   });
  //   return response.data.symbolType;
  // };

  getSymbol = async (componentId: string, symbolId: string): Promise<any> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getSymbol',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data;
  };

  // getSymbols = async (componentId: string, symbolIds: string[]): Promise<any[]> => {
  //   const response = await transceiver.send({
  //     path: this.path,
  //     method: 'getSymbols',
  //     data: {
  //       componentId,
  //       symbolIds
  //     }
  //   });
  //   return response.data;
  // };
}

export const symbolApi = new SymbolApi();

export type { SymbolProps, ISymbol };

export default SymbolApi;
