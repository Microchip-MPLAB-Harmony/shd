import { TypedUseSelectorHook } from 'react-redux';
export declare const store: import("@reduxjs/toolkit/dist/configureStore").ToolkitStore<{
    adc1: import("@reduxjs/toolkit").EntityState<import("../symbol/api/SymbolApi").ISymbol> & {
        status: string;
        error: null;
    };
    adc2: import("@reduxjs/toolkit").EntityState<import("../symbol/api/SymbolApi").ISymbol> & {
        status: string;
        error: null;
    };
}, import("redux").AnyAction, [import("@reduxjs/toolkit").ThunkMiddleware<{
    adc1: import("@reduxjs/toolkit").EntityState<import("../symbol/api/SymbolApi").ISymbol> & {
        status: string;
        error: null;
    };
    adc2: import("@reduxjs/toolkit").EntityState<import("../symbol/api/SymbolApi").ISymbol> & {
        status: string;
        error: null;
    };
}, import("redux").AnyAction, undefined>]>;
export type RootState = ReturnType<typeof store.getState>;
export declare const useAppDispatch: () => typeof store.dispatch;
export declare const useAppSelector: TypedUseSelectorHook<RootState>;
