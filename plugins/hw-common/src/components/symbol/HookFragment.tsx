export {};
// import { ISymbol, SymbolProps } from '../../symbol/api/SymbolApi';
// import useBooleanSymbol from '../../symbol/hook/useBooleanSymbol';
// import { UpdateProps } from './util';
// import { BooleanSymbol } from '../../symbol/api/BooleanSymbolApi';
// import { useEffect, useState } from 'react';
// import { symbolUtilApi } from '../../symbol/api';
// import { toSymbolValueListener } from '../../event/EventListenerFactory';
// import { EventFilter } from '../../event/EventInterfaces';
// import { SymbolValueChangedEvent } from '../../event/SymbolValueChangedEvent';

// function HookFragment<D>(
//   props: { componentId: string; symbolIds: string[] } & UpdateProps<BooleanSymbol, D>
// ) {
//   const { componentId, symbolIds, onStateUpdate, userData } = props;
//   const [symbols, setSymbols] = useState<ISymbol[]>([]);

//   useEffect(() => {
//     symbolUtilApi.getSymbols(componentId, symbolIds).then(setSymbols);

//     const valueListeners = symbolIds.map((symbolId) =>
//       toSymbolValueListener(onSymbolValueChanged, {
//         componentId,
//         symbolId
//       } as EventFilter)
//     );
//     valueListeners.map((listener) => eventAgent.addEventListener(listener));
//     return () => {
//       eventAgent.removeEventListener(valueListener);
//     };
//   }, []);

//   useEffect(() => {
//     onStateUpdate?.(booleanSymbolHook as BooleanSymbol, userData);
//   }, [booleanSymbolHook.value]);
//   function updateHandler(state: ConfigSymbol<any>, userData?: string): void {
//     log('Symbol Update: ' + JSON.stringify(state) + '\nuser Data : ' + JSON.stringify(userData));
//   }

//   const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
//     const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
//     if (result === null) {
//       // accept the event value and set it in local state
//       setValue(event.data.symbol.value);
//     } else if (typeof result === 'boolean') {
//       // use the result to trigger the DB task again.
//       booleanSymbolApi.setValue(componentId, symbolId, result);
//     }
//   };

//   return (
//     <>
//       {symbolIds.map((e) => (
//         <></>
//       ))}
//     </>
//   );
// }

// export default HookFragment;
