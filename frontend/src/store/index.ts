import { configureStore } from "@reduxjs/toolkit";

import { clinicalTrialsApi } from "./clinicalTrialsApi";

export const store = configureStore({
  reducer: {
    [clinicalTrialsApi.reducerPath]: clinicalTrialsApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(clinicalTrialsApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
