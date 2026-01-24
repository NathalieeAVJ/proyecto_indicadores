<template>
  <v-container class="fill-height bg-background" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12 rounded-lg pa-4">
          <v-card-text class="pa-8">
            <div class="text-center mb-6">
              <v-img
                src="/logo.png"
                max-width="180"
                class="mx-auto"
                style="mix-blend-mode: multiply;"
              ></v-img>
            </div>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="Usuario"
                name="login"
                prepend-icon="mdi-account"
                type="text"
                required
              ></v-text-field>

              <v-text-field
                v-model="password"
                id="password"
                label="Contraseña"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                required
              ></v-text-field>
              
              <v-alert v-if="error" type="error" dense class="mt-2">
                {{ error }}
              </v-alert>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" :loading="loading" @click="handleLogin">Entrar</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    await authStore.login(username.value, password.value);
    router.push('/');
  } catch (err) {
    error.value = 'Credenciales inválidas o error de conexión.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.fill-height {
  background-color: #F3E5F5 !important;
}
</style>
