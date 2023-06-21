import { symbolUtilApi } from '../api';

class DatabaseCache {
  private readonly _symbolIds: string[] = [];
  private readonly _symbols: Map<string, any> = new Map();

  constructor(private readonly _componentId: string) {}

  registerSymbol(symbolId: string) {
    this._symbolIds.push(symbolId);
  }

  registerSymbols(symbolIds: string[]) {
    symbolUtilApi.getSymbols(this._componentId, symbolIds).then((symbols: any[]) => {
      symbols.forEach((symbol) => this._symbols.set(symbol.symbolId, symbol));
    });

    this._symbolIds.concat(symbolIds);
  }

  findSymbol(componentId: string, symbolId: string): any | undefined {
    if (componentId !== this._componentId) return;

    return undefined;
  }

  get componentId() {
    return this._componentId;
  }
}
