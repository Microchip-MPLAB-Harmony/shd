interface EventFilter {
    componentId?: string;
    symbolId?: string;
}
interface EventListener {
    eventName: string;
    eventFilter?: EventFilter;
    eventConsumer: (e: any) => void;
}
export type { EventFilter, EventListener };
