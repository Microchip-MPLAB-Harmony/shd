import { transceiver } from '../../txrx/Transceiver';
import ConfigSymbolApi, { ConfigSymbol } from './ConfigSymbolApi';
import { log } from '@mplab_harmony/harmony-plugin-core-service';

interface KeyValueSetSymbol extends ConfigSymbol<number> {
  optionPairs: OptionPair[];
  displayMode: DisplayMode;
  selectedOptionPair: OptionPair;
}

interface OptionPair {
  key: string;
  value: string;
  description: string;
}

export enum DisplayMode {
  Key = 'Key',
  Value = 'Value',
  Description = 'Description'
}

class KeyValueSetSymbolApi extends ConfigSymbolApi {
  readonly path: string;

  constructor(path?: string) {
    super(path);
    this.path = path || 'KeyValueSetSymbol';
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

  getOptionPairs = async (componentId: string, symbolId: string): Promise<OptionPair[]> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getOptionPairs',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.optionPairs as OptionPair[];
  };

  getSelectedOptionPair = async (componentId: string, symbolId: string): Promise<OptionPair> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getSelectedOptionPair',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.selectedOptionPair as OptionPair;
  };

  getDisplayMode = async (componentId: string, symbolId: string): Promise<string> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getDisplayMode',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data.displayMode as string;
  };

  setDisplayMode = async (
    componentId: string,
    symbolId: string,
    displayMode: DisplayMode
  ): Promise<void> => {
    transceiver.send({
      path: this.path,
      method: 'setDisplayMode',
      data: {
        componentId,
        symbolId,
        displayMode
      }
    });
    return;
  };

  getKeyValueSetSymbol = async (
    componentId: string,
    symbolId: string
  ): Promise<KeyValueSetSymbol> => {
    const response = await transceiver.send({
      path: this.path,
      method: 'getKeyValueSetSymbol',
      data: {
        componentId,
        symbolId
      }
    });
    return response.data as KeyValueSetSymbol;
  };
}

export const keyValueSetSymbolApi = new KeyValueSetSymbolApi();

export type { KeyValueSetSymbol, OptionPair };

export default KeyValueSetSymbolApi;
