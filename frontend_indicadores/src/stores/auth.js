import { defineStore } from 'pinia';
import api from '@/services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    async login(username, password) {
        try {
            // Adjust endpoint based on how we implement auth. 
            // For now assuming we might use djoser or simple obtain_auth_token
            // But we didn't install djoser. We need a token endpoint in Django.
            // I will implement a simple login View in Django later if needed, or stick to Basic Auth for testing?
            // BETTER: Add authtoken to Django.
            
            // For this step, I'll assume we hit an endpoint.
            // Since we didn't setup token auth in Django yet (DRF TokenAuthentication), I should do that in the backend?
            // Waiting... I should probably add rest_framework.authtoken to INSTALLED_APPS in settings.py first.
            // But let's write this store assuming we will have it.
            
            const response = await api.post('/api-token-auth/', { username, password }, { baseURL: 'http://localhost:8000' }); 
            
            if (response && response.token) {
                this.token = response.token;
                localStorage.setItem('token', this.token);
                
                // Fetch user details
                const userProfile = await api.get('users/me/');
                this.user = userProfile;
                localStorage.setItem('user', JSON.stringify(this.user));
            } else {
                throw new Error('No se recibió token del servidor');
            }
        } catch (error) {
            throw error;
        }
    },
    logout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    },
  },
});
