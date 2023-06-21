import { PayloadAction, createSlice } from '@reduxjs/toolkit';

type Component = {
  componentId: string;
  value1: string;
  value2: string;
};

const initialState: Component = {
  componentId: 'COMP1',
  value1: 'VALUE1',
  value2: 'VALUE2',
};

const componentSlice = createSlice({
  name: 'components',
  initialState,
  reducers: {
    setComponentId(state, action: PayloadAction<{ componentId: string }>) {
      const { componentId } = action.payload;
      state.componentId = componentId;
    },
    setValue1(state, action: PayloadAction<{ value1: string }>) {
      const { value1 } = action.payload;
      state.value1 = value1;
    },
    setValue2(state, action: PayloadAction<{ value2: string }>) {
      const { value2 } = action.payload;
      state.value2 = value2;
    },
  },
});

export const { setComponentId, setValue1, setValue2 } = componentSlice.actions;
export default componentSlice.reducer;
