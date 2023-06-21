export function createClassResolver(...classMaps: { [key: string]: string }[]) {
  return function (...classNames: string[]): string {
    return classNames
      .map((className) =>
        classMaps
          .map((classMap) => classMap[className])
          .filter(Boolean)
          .join(' ')
      )
      .join(' ');
  };
}
