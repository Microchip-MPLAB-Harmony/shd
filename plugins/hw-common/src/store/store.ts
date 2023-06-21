import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

import databaseReducer from '../slices/databaseSlice';
import component from '../slices/componentSlice';

export const store = configureStore({
  reducer: {
    adc1: databaseReducer,
    adc2: databaseReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export const useAppDispatch: () => typeof store.dispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
