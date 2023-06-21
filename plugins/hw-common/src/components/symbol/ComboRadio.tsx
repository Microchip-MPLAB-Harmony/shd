import { RadioButton, RadioButtonProps } from 'primereact/radiobutton';
import { ComboSymbolHook } from '../../symbol/hook/useComboSymbol';

const ComboRadio = (
  props: RadioButtonProps & { comboSymbolHook: ComboSymbolHook } & {
    classPrefix: string;
    classResolver?: (className: string) => string;
  }
) => {
  const { value, options, readOnly, visible, writeValue } = props.comboSymbolHook;
  const { comboSymbolHook, classPrefix, classResolver, ...onlyRadioButtonProps } = props;

  return !(props.hidden ?? !visible) ? (
    <>
      {options.map((option, i) => (
        <RadioButton
          key={option}
          inputId={option}
          name={classPrefix}
          disabled={readOnly}
          value={option}
          onChange={(e) => writeValue(option)}
          checked={option === value}
          {...onlyRadioButtonProps}
          className={classResolver ? classResolver(`${classPrefix}${i}`) : `${classPrefix}${i}`}
        />
      ))}
    </>
  ) : (
    <></>
  );
};

export default ComboRadio;
