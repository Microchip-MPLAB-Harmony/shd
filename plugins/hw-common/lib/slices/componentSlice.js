"use strict";
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
exports.setValue2 = exports.setValue1 = exports.setComponentId = void 0;
const toolkit_1 = require("@reduxjs/toolkit");
const initialState = {
    componentId: 'COMP1',
    value1: 'VALUE1',
    value2: 'VALUE2',
};
const componentSlice = (0, toolkit_1.createSlice)({
    name: 'components',
    initialState,
    reducers: {
        setComponentId(state, action) {
            const { componentId } = action.payload;
            state.componentId = componentId;
        },
        setValue1(state, action) {
            const { value1 } = action.payload;
            state.value1 = value1;
        },
        setValue2(state, action) {
            const { value2 } = action.payload;
            state.value2 = value2;
        },
    },
});
_a = componentSlice.actions, exports.setComponentId = _a.setComponentId, exports.setValue1 = _a.setValue1, exports.setValue2 = _a.setValue2;
exports.default = componentSlice.reducer;
