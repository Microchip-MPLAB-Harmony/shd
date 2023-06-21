import { MouseEvent } from 'react';
interface PannableContainer {
    ref: React.RefObject<HTMLDivElement>;
    props: {
        onMouseDown: (e: MouseEvent<HTMLDivElement>) => void;
        onMouseMove: (e: MouseEvent<HTMLDivElement>) => void;
        onMouseUp: () => void;
        onMouseOut: () => void;
        style: React.CSSProperties;
    };
}
declare function usePannableContainer(): PannableContainer;
export default usePannableContainer;
