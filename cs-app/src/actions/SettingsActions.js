
export function addFriend(name) {
  return {
    type: "add",
    name
  };
}

export function deleteFriend(id) {
  return {
    type: "del",
    id
  };
}

export function starFriend(id) {
  return {
    type: "put",
    id
  };
}
