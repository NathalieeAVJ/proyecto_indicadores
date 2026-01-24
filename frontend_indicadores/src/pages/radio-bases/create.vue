<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Nueva Radiobase</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.name" label="Nombre de la Radiobase" required></v-text-field>
              <v-text-field v-model="form.code" label="Código de Estación" required></v-text-field>
              <v-text-field v-model="form.location" label="Ubicación / Dirección"></v-text-field>
              <v-row>
                <v-col><v-text-field v-model="form.latitude" label="Latitud" type="number" step="0.000001"></v-text-field></v-col>
                <v-col><v-text-field v-model="form.longitude" label="Longitud" type="number" step="0.000001"></v-text-field></v-col>
              </v-row>

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
    code: '',
    location: '',
    latitude: null,
    longitude: null,
});

const loading = ref(false);
const router = useRouter();

const submit = async () => {
    loading.value = true;
    try {
        await api.post('radio-bases/', form.value);
        router.push('/radio-bases');
    } catch (e) {
        console.error(e);
        alert('Error al crear radiobase');
    } finally {
        loading.value = false;
    }
};
</script>
