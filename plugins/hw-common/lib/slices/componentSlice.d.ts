type Component = {
    componentId: string;
    value1: string;
    value2: string;
};
export declare const setComponentId: import("@reduxjs/toolkit").ActionCreatorWithPayload<{
    componentId: string;
}, "components/setComponentId">, setValue1: import("@reduxjs/toolkit").ActionCreatorWithPayload<{
    value1: string;
}, "components/setValue1">, setValue2: import("@reduxjs/toolkit").ActionCreatorWithPayload<{
    value2: string;
}, "components/setValue2">;
declare const _default: import("redux").Reducer<Component, import("redux").AnyAction>;
export default _default;
