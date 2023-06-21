export declare function processUiEvent<T>(uiValue: T, syncValue: T | undefined): T | undefined;
export declare function processDBEvent<T>(dbValue: T, syncValue: T | undefined, valueBackup: T): T | null | undefined;
declare class EventSynchronizer<T> {
    private _valueBackup;
    private syncValue;
    constructor(_valueBackup: T);
    get valueBackup(): T;
    set valueBackup(value: T);
    processUiEvent(uiValue: T): T | undefined;
    processDBEvent(dbValue: T): T | null | undefined;
}
export default EventSynchronizer;
