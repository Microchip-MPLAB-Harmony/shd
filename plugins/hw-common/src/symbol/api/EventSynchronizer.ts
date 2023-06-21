import { error } from '@mplab_harmony/harmony-plugin-core-service';

class EventSynchronizer<T> {
  private syncValue: T | undefined = undefined;

  // initialize the backup value with Hook's local state.
  constructor(private _valueBackup: T) {}

  get valueBackup(): T {
    return this._valueBackup;
  }

  set valueBackup(value: T) {
    this._valueBackup = value;
  }
  /**
   *
   * @param uiValue
   * @returns undefined: ignore
   *          T (type of the event value): use it to trigger the DB task.
   */
  processUiEvent(uiValue: T): T | undefined {
    if (this.syncValue === undefined) {
      this.syncValue = uiValue;
      return uiValue;
    }
  }
  /**
   *
   * @param dbValue
   * @returns null: set the event Value in the local state value.
   *          undefined: ignore
   *          T (type of the event value): use it to trigger the DB task again.
   */
  processDBEvent(dbValue: T): T | null | undefined {
    // const a = `value: ${this._valueBackup}, syncValue: ${this.syncValue}, event.data.value: ${dbValue}`;
    // log('=======================Event RECEIVED : ' + a);
    if (this.syncValue === undefined) {
      this.valueBackup = dbValue;
      // log('=======================Event Used : ' + a);
      return null;
    } else if (this.syncValue === dbValue) {
      if (this.valueBackup !== this.syncValue) {
        this.syncValue = this.valueBackup;
        // log('=======================Event Ignored & sending Value : ' + a);
        return this.valueBackup;
      } else {
        // log('=======================Event Ignored : ' + a);
        this.syncValue = undefined;
      }
    } else {
      error(
        `Event Sync Issue: Expected Value: ${JSON.stringify(
          this.syncValue
        )}, Received: ${JSON.stringify(dbValue)}`
      );
    }
  }
}

export default EventSynchronizer;
