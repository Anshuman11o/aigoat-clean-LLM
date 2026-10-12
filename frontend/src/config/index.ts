// Modified for this distribution.
//@ts-nocheck
             
import axios from 'axios';

                                                    
                                                                                          
const FLASK_API_URL = "PLACE_HOLDER";

                                         
                            
                   
               
                                          
       
      
export const getToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

export const storeApi = axios.create({
  baseURL: FLASK_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

storeApi.interceptors.request.use(
  config => {
    const token = getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);
