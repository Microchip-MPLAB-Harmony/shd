import {
  AsyncThunk,
  PayloadAction,
  createAsyncThunk,
  createEntityAdapter,
  createSlice
} from '@reduxjs/toolkit';
import { ISymbol, symbolApi, symbolUtilApi } from '../symbol/api';

type TComponent = {
  componentId: string;
  symbols: unknown[];
};

const initialState = {
  components: [] as TComponent[]
};

const fetchSymbols = createAsyncThunk(
  'symbol/fetchSymbols',
  async (id: { componentId: string; symbolIds: string[] }) => {
    return await symbolUtilApi.getSymbols(id.componentId, id.symbolIds);
  }
);

const fetchSymbol = createAsyncThunk(
  'symbol/fetchSymbol',
  async (id: { componentId: string; symbolId: string }) => {
    return await symbolApi.getSymbol(id.componentId, id.symbolId);
  }
);

const symbolAdapter = createEntityAdapter<ISymbol>({
  selectId: (symbol: ISymbol) => `${symbol.componentId}_${symbol.symbolId}`
});

const databaseSlice = createSlice({
  name: 'database',
  initialState: symbolAdapter.getInitialState({ status: 'idle', error: null }),

  reducers: {
    registerSymbol: symbolAdapter.addOne,
    addSymbol(state, action: PayloadAction<{ componentId: string; symbolId: string }>) {
      const { componentId, symbolId } = action.payload;

      // const component = state.components.find(
      //   (e) => e.componentId == componentId
      // );

      // component?.symbols.push(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder.addCase(fetchSymbol.fulfilled, (state, action) => {
      symbolAdapter.addOne(state, action.payload);
    });
  }
  // extraReducers: (builder) => {
  //   builder
  //   .
  //     .addCase(fetchSymbols., (state) => {
  //       state.status = 'loading';
  //     })
  //     .addCase(fetchSymbols.fulfilled, (state, action) => {
  //       state.status = 'succeeded';
  //       symbolAdapter.setAll(state, action.payload);
  //     })
  //     .addCase(fetchSymbols.rejected, (state, action) => {
  //       state.status = 'failed';
  //       state.error = action.error.message;
  //     });
  // },
});

export const { addSymbol } = databaseSlice.actions;
export default databaseSlice.reducer;

export const { selectById: selectSymbol } = symbolAdapter.getSelectors();
