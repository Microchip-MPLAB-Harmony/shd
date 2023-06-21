import { ISymbol, symbolUtilApi } from '../../symbol/api';
import CheckBoxDefault from './CheckBoxDefault';
import InputNumberDefault from './InputNumberDefault';
import { useEffect, useState } from 'react';
import DropDownDefault from './DropDownDefault';
import ComboBoxDefault from './ComboBoxDefault';
import InputTextDefault from './InputTextDefault';
import CommentLabelDefault from './CommentLabelDefault';

const DefaultControl = (props: { symbol: ISymbol; className?: string }) => {
  const { componentId, symbolId, symbolType } = props.symbol;
  switch (symbolType) {
    case 'BooleanSymbol': {
      return (
        <CheckBoxDefault
          componentId={componentId}
          symbolId={symbolId}
          className={props.className}
        />
      );
    }
    case 'IntegerSymbol': {
      return (
        <InputNumberDefault
          componentId={componentId}
          symbolId={symbolId}
          className={props.className}
        />
      );
    }
    case 'KeyValueSetSymbol': {
      return (
        <DropDownDefault
          componentId={componentId}
          symbolId={symbolId}
          className={props.className}
        />
      );
    }
    case 'CommentSymbol': {
      return (
        <CommentLabelDefault
          componentId={componentId}
          symbolId={symbolId}
          className={props.className}
        />
      );
    }
    case 'ComboSymbol': {
      return (
        <ComboBoxDefault
          componentId={componentId}
          symbolId={symbolId}
          className={props.className}
        />
      );
    }
    case 'StringSymbol': {
      return (
        <InputTextDefault
          componentId={componentId}
          symbolId={symbolId}
          className={props.className}
        />
      );
    }
    default: {
      return <div>Default Control Not Available for the symbol Type {symbolType}</div>;
    }
  }
};

const DefaultControls = (props: { componentId: string; symbolIds: string[] }) => {
  const [symbols, setSymbols] = useState<ISymbol[]>([]);

  useEffect(() => {
    symbolUtilApi.getSymbolTypes(props.componentId, props.symbolIds).then((e: ISymbol[]) => {
      setSymbols(e);
    });
  }, []);

  return (
    <>
      {symbols.map((symbol: ISymbol) => (
        <DefaultControl
          key={symbol.symbolId}
          symbol={symbol}
        />
      ))}
    </>
  );
};

export { DefaultControl, DefaultControls };
