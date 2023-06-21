"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.selectSymbol = exports.addSymbol = void 0;
const toolkit_1 = require("@reduxjs/toolkit");
const api_1 = require("../symbol/api");
const initialState = {
    components: []
};
const fetchSymbols = (0, toolkit_1.createAsyncThunk)('symbol/fetchSymbols', (id) => __awaiter(void 0, void 0, void 0, function* () {
    return yield api_1.symbolUtilApi.getSymbols(id.componentId, id.symbolIds);
}));
const fetchSymbol = (0, toolkit_1.createAsyncThunk)('symbol/fetchSymbol', (id) => __awaiter(void 0, void 0, void 0, function* () {
    return yield api_1.symbolApi.getSymbol(id.componentId, id.symbolId);
}));
const symbolAdapter = (0, toolkit_1.createEntityAdapter)({
    selectId: (symbol) => `${symbol.componentId}_${symbol.symbolId}`
});
const databaseSlice = (0, toolkit_1.createSlice)({
    name: 'database',
    initialState: symbolAdapter.getInitialState({ status: 'idle', error: null }),
    reducers: {
        registerSymbol: symbolAdapter.addOne,
        addSymbol(state, action) {
            const { componentId, symbolId } = action.payload;
        }
    },
    extraReducers: (builder) => {
        builder.addCase(fetchSymbol.fulfilled, (state, action) => {
            symbolAdapter.addOne(state, action.payload);
        });
    }
});
exports.addSymbol = databaseSlice.actions.addSymbol;
exports.default = databaseSlice.reducer;
exports.selectSymbol = symbolAdapter.getSelectors().selectById;
