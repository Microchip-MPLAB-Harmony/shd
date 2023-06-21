export {};
// import { useEffect } from 'react';
// import { SymbolValueChangedEvent } from '../event/SymbolValueChangedEvent';
// import { useSelector } from 'react-redux';
// import { selectSymbol } from '../slices/databaseSlice';
// import { processDBEvent } from './event-sync';

// const useGlobalSymbolListener = () => {
//   selectSymbol('sdfasf');

//   const symbols = useSelector((state) => state.symbols);

//   useEffect(() => {
//     return () => {
//       second;
//     };
//   }, [third]);

//   const onSymbolValueChanged = (event: SymbolValueChangedEvent) => {
//     const result = eventSynchronizer.current.processDBEvent(event.data.symbol.value);
//     processDBEvent(event.data.symbol.value, )
//     if (result === null) {
//       // accept the event value and set it in local state
//       setValue(event.data.symbol.value);
//     } else if (typeof result === 'boolean') {
//       // use the result to trigger the DB task again.
//       booleanSymbolApi.setValue(componentId, symbolId, result);
//     }
//   };
// };

// export default useGlobalSymbolListener;
