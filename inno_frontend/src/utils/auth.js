export const saveUserData = (token, user) => {
  // Make sure token is properly trimmed and not null/undefined
  if (token) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    console.log('Token saved successfully:', token.substring(0, 15) + '...');
    console.log('User data saved:', user);
  } else {
    console.error('Attempted to save null/undefined token');
  }
};

export const getToken = () => {
  const token = localStorage.getItem('token');
  if (token) {
    console.log('Retrieved token successfully:', token.substring(0, 15) + '...');
  } else {
    console.log('No token found in localStorage');
  }
  return token;
};

export const isAuthenticated = () => {
  const token = getToken();
  return !!token;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  console.log('Logged out, tokens cleared');
};

export const getUserData = () => {
  const user = localStorage.getItem('user');
  if (user) {
    try {
      const userData = JSON.parse(user);
      console.log('Retrieved user data:', userData);
      return userData;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  }
  console.log('No user data found in localStorage');
  return null;
};