type FirstType = {
    common: string;
    firstProperty: string;
};
type SecondType = {
    common: string;
    secondProperty: number;
};
type UnionType = FirstType | SecondType;
declare const variable: UnionType;
declare const value1: UnionType;
declare const value2: UnionType;
declare const value3: UnionType;
