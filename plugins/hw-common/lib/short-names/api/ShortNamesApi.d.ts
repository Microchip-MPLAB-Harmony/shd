declare class ShortNamesApi {
    readonly path: string;
    generateShortNamesTemplate: (componentId: string, symbolId: string) => Promise<any>;
    getResolvedShortNamesTemplate: (fileName: string) => Promise<any>;
    applyShortNames: (componentId: string, symbolId: string, shortNames: any) => Promise<void>;
}
export declare const shortNamesApi: ShortNamesApi;
export default ShortNamesApi;
