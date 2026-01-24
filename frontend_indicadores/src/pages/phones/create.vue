<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Nuevo Número</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.number" label="Número Telefónico" required></v-text-field>
              <v-text-field v-model="form.description" label="Descripción / Alias"></v-text-field>
              <v-text-field v-model="form.department" label="Departamento"></v-text-field>
              <v-text-field v-model="form.location" label="Ubicación"></v-text-field>

              <v-btn color="primary" type="submit" :loading="loading" class="mt-4">Guardar</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';

const form = ref({
    number: '',
    description: '',
    department: '',
    location: '',
});

const loading = ref(false);
const router = useRouter();

const submit = async () => {
    loading.value = true;
    try {
        await api.post('phones/', form.value);
        router.push('/phones');
    } catch (e) {
        console.error(e);
        alert('Error al crear número');
    } finally {
        loading.value = false;
    }
};
</script>
