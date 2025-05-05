
interface TokenData {
  access_token: string;
  realmId:string;
  state:string
}

export const saveTokens = (tokenData: TokenData): void => {
  const dataToSave = {
    ...tokenData,
    timestamp: Date.now(),
  };
  localStorage.setItem('qbTokens', JSON.stringify(dataToSave));
};

export const getTokens = (): TokenData | null => {
  const tokens = localStorage.getItem('qbTokens');
  if (!tokens) return null;
  return JSON.parse(tokens);
};
export const isTokenExpired = (): boolean => {
  const tokenStr = localStorage.getItem("qbTokens");
  if (!tokenStr) return true;

  const token = JSON.parse(tokenStr);
  const tokenIssuedAt = token.timestamp;
  const expiresIn = 3600 * 1000; // 1 hour in ms

  return Date.now() > tokenIssuedAt + expiresIn;
};


export const getExpiryTime = (): Date | null => {
  const tokens = getTokens();
  if (!tokens || !tokens.timestamp || !tokens.expires_in) return null;

  return new Date(tokens.timestamp + (tokens.expires_in * 1000));
};

export const clearTokens = (): void => {
  localStorage.removeItem('qbTokens');
};

export const getAccessToken = (): string | null => {
  const tokens = getTokens();
  return tokens?.access_token || null;
};
