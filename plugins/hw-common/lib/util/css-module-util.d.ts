export declare function createClassResolver(...classMaps: {
    [key: string]: string;
}[]): (...classNames: string[]) => string;
