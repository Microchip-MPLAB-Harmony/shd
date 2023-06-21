// import { useEffect, useRef, useState } from 'react';
// import { booleanSymbolApi } from '../api/BooleanSymbolApi';
// import { useContext } from 'react';
// import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';
// import {
//   toSymbolValueListener,
//   toSymbolVisibleListener,
// } from '../../event/EventListenerFactory';
// import { EventAgentContext } from '../../txrx/EventService';
// import { EventFilter } from '../../event/EventInterfaces';
// import { log } from '@mplab_harmony/harmony-plugin-core-service';
// import { SymbolProps } from '../api/SymbolApi';
// import EventSynchronizer from '../api/EventSynchronizer';
// import useSymbolObservables from './useSymbolObservables';

// const useBooleanSymbol = ({ componentId, symbolId }: SymbolProps) => {
//   const sadf = useBetween(useSymbolObservables);

//   const eventAgent = useContext(EventAgentContext);

//   const [value, setValue] = useState(false);
//   const eventSynchronizer = useRef(new EventSynchronizer(value));
//   const [visible, setVisible] = useState(false);
//   const [label, setLabel] = useState('');
//   const [description, setDescription] = useState('');
//   const [readOnly, setReadOnly] = useState(false);

//   useEffect(() => {
//     use;

//     initFromDB();

//     const valueListener = toSymbolValueListener(onSymbolValueChanged, {
//       componentId,
//       symbolId,
//     } as EventFilter);
//     eventAgent.addEventListener(valueListener);
//     return () => {
//       eventAgent.removeEventListener(valueListener);
//     };
//   }, []);

//   const initFromDB = () => {
//     booleanSymbolApi
//       .getBooleanSymbol(componentId, symbolId)
//       .then(({ value, visible, label, description, readOnly }) => {
//         setValue(value);
//         setVisible(visible);
//         setLabel(label);
//         setDescription(description);
//         setReadOnly(readOnly);
//       });
//   };

//   const writeValue = (newValue: boolean) => {
//     if (newValue === value) {
//       return;
//     }

//     eventSynchronizer.current.valueBackup = newValue;
//     setValue(newValue);
//     const result = eventSynchronizer.current.processUiEvent(newValue);
//     if (typeof result === 'boolean') {
//       // use the result to trigger the DB task.
//       booleanSymbolApi.setValue(componentId, symbolId, result);
//     }
//   };

//   const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
//     const result = eventSynchronizer.current.processDBEvent(
//       event.data.symbol.value
//     );
//     if (result === null) {
//       // accept the event value and set it in local state
//       setValue(event.data.symbol.value);
//     } else if (typeof result === 'boolean') {
//       // use the result to trigger the DB task again.
//       booleanSymbolApi.setValue(componentId, symbolId, result);
//     }
//   };

//   const onSymbolVisualChanged = (event: SymbolValueChangedEvent) => {
//     // setVisible(event.visibe);
//   };

//   const onSymbolStateChanged = (event: SymbolValueChangedEvent) => {
//     setValue(event.value);
//   };

//   return {
//     componentId,
//     symbolId,
//     value,
//     writeValue,
//     visible,
//     label,
//     description,
//     readOnly,
//   } as BooleanSymbolHook;
// };

// export interface BooleanSymbolHook {
//   componentId: string;
//   symbolId: string;
//   value: boolean;
//   writeValue: (newValue: boolean) => void;
//   visible: boolean;
//   label: string;
//   description: string;
//   readOnly: boolean;
// }

// export default useBooleanSymbol;
