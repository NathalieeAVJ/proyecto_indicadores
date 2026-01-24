<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Editar Número</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.number" label="Número Telefónico" required></v-text-field>
              <v-text-field v-model="form.description" label="Descripción / Alias"></v-text-field>
              <v-text-field v-model="form.department" label="Departamento"></v-text-field>
              <v-text-field v-model="form.location" label="Ubicación"></v-text-field>

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
    number: '',
    description: '',
    department: '',
    location: '',
});

const loading = ref(false);
const router = useRouter();
const route = useRoute();

const submit = async () => {
    loading.value = true;
    try {
        await api.put(`phones/${route.params.id}/`, form.value);
        router.push('/phones');
    } catch (e) {
        console.error(e);
        alert('Error al actualizar');
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
    try {
        const res = await api.get(`phones/${route.params.id}/`);
        form.value = res;
    } catch (e) {
        console.error(e);
    }
});
</script>
