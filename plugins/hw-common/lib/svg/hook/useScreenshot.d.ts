/// <reference types="react" />
interface ScreenshotContainer {
    ref: React.MutableRefObject<HTMLDivElement | null>;
    copyAsBlob: () => Promise<void>;
    copyAsPng: () => Promise<void>;
    copyAsSvg: () => Promise<void>;
    downloadAsSvg: (fileName: string) => Promise<void>;
}
declare function useScreehshot(): ScreenshotContainer;
export default useScreehshot;
