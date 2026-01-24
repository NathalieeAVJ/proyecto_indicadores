<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Nueva Incidencia de Radiobase</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.title" label="Asunto" required></v-text-field>
              
              <v-select
                v-model="form.radio_base"
                :items="radioBases"
                item-title="name"
                item-value="id"
                label="Radiobase Afectada"
                required
              ></v-select>
              
              <v-select
                v-model="form.failure_type"
                :items="failureTypes"
                item-title="name"
                item-value="id"
                label="Tipo de Falla"
                required
              ></v-select>
              
              <v-textarea v-model="form.description" label="Descripción"></v-textarea>
              <v-text-field v-model="form.start_date" type="datetime-local" label="Fecha Inicio"></v-text-field>
              
              <v-btn color="primary" type="submit" :loading="loading" class="mt-4">Guardar Incidencia</v-btn>
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
import { useRouter } from 'vue-router';

const form = ref({
    title: '',
    radio_base: null,
    failure_type: null,
    description: '',
    start_date: new Date().toISOString().slice(0, 16),
});

const radioBases = ref([]);
const failureTypes = ref([]);
const loading = ref(false);
const router = useRouter();

const submit = async () => {
    loading.value = true;
    try {
        await api.post('rb-incidents/', form.value);
        router.push('/rb-incidents');
    } catch (e) {
        console.error(e);
        alert('Error al crear incidencia de radiobase');
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
    try {
        const [rbRes, typesRes] = await Promise.all([
            api.get('radio-bases/'),
            api.get('failure-types/')
        ]);
        radioBases.value = rbRes;
        failureTypes.value = typesRes;
    } catch (e) {
        console.error(e);
    }
});
</script>
