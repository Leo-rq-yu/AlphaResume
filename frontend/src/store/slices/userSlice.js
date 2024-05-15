import { createSlice } from '@reduxjs/toolkit';

const userSlice = createSlice({
  name: 'user',
  initialState: {
    id: null
  },
  reducers: {
    setId: (state, action) => {
      state.id = action.payload;
    }
  }
});

export const { setId } = userSlice.actions;
export default userSlice.reducer;