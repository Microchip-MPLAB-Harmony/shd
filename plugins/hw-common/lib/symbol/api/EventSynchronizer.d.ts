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
