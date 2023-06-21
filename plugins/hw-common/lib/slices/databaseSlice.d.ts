import { ISymbol } from '../symbol/api';
export declare const addSymbol: import("@reduxjs/toolkit").ActionCreatorWithPayload<{
    componentId: string;
    symbolId: string;
}, "database/addSymbol">;
declare const _default: import("redux").Reducer<import("@reduxjs/toolkit").EntityState<ISymbol> & {
    status: string;
    error: null;
}, import("redux").AnyAction>;
export default _default;
export declare const selectSymbol: (state: import("@reduxjs/toolkit").EntityState<ISymbol>, id: import("@reduxjs/toolkit").EntityId) => ISymbol | undefined;
