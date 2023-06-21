import { WheelEvent, MouseEvent } from 'react';
export default function useZoomableContainer(): {
    ref: import("react").MutableRefObject<HTMLDivElement | null>;
    zoomIn: (value?: number) => void;
    zoomOut: (value?: number) => void;
    resetZoom: () => void;
    props: {
        onWheel: (event: WheelEvent<HTMLDivElement>) => void;
        onMouseDown: (event: MouseEvent<HTMLDivElement>) => void;
    };
};
