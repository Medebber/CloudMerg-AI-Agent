import axios from 'axios';

const API = axios.create({
  baseURL: '',
});

// Example: send a message to chatbot
export const sendMessage = async (message) => {
  const response = await API.post('/chat', { message });
  return response.data;
};

export default API;
