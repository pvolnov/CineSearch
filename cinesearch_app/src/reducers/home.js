

export  default function home(state = {list:[]}, action) {

  switch (action.type) {
    case "RECORDS_UPDATE":

      state.list =  action.data;
      return state;


    default:
      return state
  }
}
