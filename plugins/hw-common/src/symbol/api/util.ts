import { DisplayMode, OptionPair } from './KeyValueSetSymbolApi';
type AnySymbol<T> = {
  componentId: string;
  symbolId: string;
  symbolType: string;
  visible?: boolean;
  label?: string;
  description?: string;
  readOnly?: boolean;
  value?: T;
  options?: string[];
  min?: number;
  max?: number;
  optionPairs?: OptionPair[];
  displayMode?: DisplayMode;
  selectedOptionPair?: OptionPair;
};

const defaultSymbol: AnySymbol<string> = {
  componentId: 'defaultComponentId',
  symbolId: 'defaultSymbolId',
  symbolType: 'StringSymbol',
  visible: false,
  label: 'defaultLabel',
  description: 'defaultDescription',
  readOnly: true,
  value: 'defaultValue',
  options: [],
  min: 0,
  max: 0,
  optionPairs: [],
  displayMode: DisplayMode.Description,
  selectedOptionPair: {
    description: 'defaultDescription',
    key: 'defaultKey',
    value: 'defaultValue'
  }
};

function createDefaultSymbol() {
  return JSON.parse(JSON.stringify(defaultSymbol));
}

export type { AnySymbol };
export { createDefaultSymbol };
