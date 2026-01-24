<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Editar Tipo de Falla</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.name" label="Nombre" required></v-text-field>
              <v-textarea v-model="form.description" label="Descripción"></v-textarea>
              <v-btn color="primary" type="submit" :loading="loading" class="mt-4">Actualizar</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useRouter, useRoute } from 'vue-router';

const form = ref({
    name: '',
    description: '',
});

const loading = ref(false);
const router = useRouter();
const route = useRoute();

const submit = async () => {
    loading.value = true;
    try {
        await api.put(`failure-types/${route.params.id}/`, form.value);
        router.push('/failure-types');
    } catch (e) {
        console.error(e);
        alert('Error al actualizar');
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
  try {
      const res = await api.get(`failure-types/${route.params.id}/`);
      form.value = res;
  } catch (e) {
      console.error(e);
  }
});
</script>
