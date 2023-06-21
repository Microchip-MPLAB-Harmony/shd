import { RadioButton, RadioButtonProps } from 'primereact/radiobutton';
import { KeyValueSetSymbolHook } from '../../symbol/hook/useKeyValueSetSymbol';

const KeyValueSetRadio = (
  props: RadioButtonProps & { keyValueSetSymbolHook: KeyValueSetSymbolHook } & {
    classPrefix: string;
    classResolver?: (className: string) => string;
  }
) => {
  const { selectedOption, options, readOnly, visible, writeValue } = props.keyValueSetSymbolHook;
  const { keyValueSetSymbolHook, classPrefix, classResolver, ...onlyRadioButtonProps } = props;

  return !(props.hidden ?? !visible) ? (
    <>
      {options.map((option, i) => (
        <RadioButton
          key={option}
          inputId={option}
          name={classPrefix}
          disabled={readOnly}
          value={option}
          tooltip={option}
          onChange={(e) => writeValue(option)}
          checked={option === selectedOption}
          {...onlyRadioButtonProps}
          className={classResolver ? classResolver(`${classPrefix}${i}`) : `${classPrefix}${i}`}
        />
      ))}
    </>
  ) : (
    <></>
  );
};

export default KeyValueSetRadio;
