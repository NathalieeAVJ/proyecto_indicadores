<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Nuevo Tipo de Falla</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.name" label="Nombre" required></v-text-field>
              <v-textarea v-model="form.description" label="Descripción"></v-textarea>
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
    name: '',
    description: '',
});

const loading = ref(false);
const router = useRouter();

const submit = async () => {
    loading.value = true;
    try {
        await api.post('failure-types/', form.value);
        router.push('/failure-types');
    } catch (e) {
        console.error(e);
        alert('Error al crear tipo de falla');
    } finally {
        loading.value = false;
    }
};
</script>
