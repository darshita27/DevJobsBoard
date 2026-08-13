export interface User {
  id: number;
  username: string;
  email: string;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}
