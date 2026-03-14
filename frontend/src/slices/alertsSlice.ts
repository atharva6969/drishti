import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  status: string;
  created_at: string;
}

interface AlertsState {
  alerts: Alert[];
  unreadCount: number;
}

const initialState: AlertsState = {
  alerts: [],
  unreadCount: 0,
};

const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    addAlert: (state, action: PayloadAction<Alert>) => {
      state.alerts.unshift(action.payload);
      state.unreadCount += 1;
    },
    setAlerts: (state, action: PayloadAction<Alert[]>) => {
      state.alerts = action.payload;
    },
    markAllRead: (state) => {
      state.unreadCount = 0;
    },
    clearAlert: (state, action: PayloadAction<number>) => {
      state.alerts = state.alerts.filter(a => a.id !== action.payload);
    },
  },
});

export const { addAlert, setAlerts, markAllRead, clearAlert } = alertsSlice.actions;
export default alertsSlice.reducer;
