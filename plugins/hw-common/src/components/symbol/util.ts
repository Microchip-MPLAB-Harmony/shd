export type UpdateProps<T, D> = {
  userData?: D;
  onStateUpdate?: (state: T, userData?: D) => void;
};
