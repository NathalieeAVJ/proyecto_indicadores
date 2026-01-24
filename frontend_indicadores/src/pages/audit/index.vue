<template>
  <v-container>
    <v-row>
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Auditoría de Sistema</h1>
        <v-btn icon="mdi-refresh" @click="fetchLogs" :loading="loading"></v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-data-table
            :headers="headers"
            :items="logs"
            :loading="loading"
          >
            <template v-slot:item.action="{ item }">
              <v-chip :color="getActionColor(item.action)" size="small">
                {{ getActionLabel(item.action) }}
              </v-chip>
            </template>
            <template v-slot:item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { formatDate } from '@/utils/format';

const logs = ref([]);
const loading = ref(true);

const headers = [
  { title: 'Fecha', key: 'created_at' },
  { title: 'Usuario', key: 'username' },
  { title: 'Acción', key: 'action' },
  { title: 'Módulo', key: 'module' },
  { title: 'Descripción', key: 'description' },
  { title: 'IP', key: 'ip_address' },
];

const getActionColor = (a) => {
  if (a === 'create') return 'success';
  if (a === 'update') return 'info';
  if (a === 'delete') return 'error';
  return 'grey';
};

const getActionLabel = (a) => {
  switch(a) {
    case 'create': return 'CREACIÓN';
    case 'update': return 'ACTUALIZACIÓN';
    case 'delete': return 'ELIMINACIÓN';
    case 'login': return 'INICIO SESIÓN';
    default: return (a || '').toUpperCase();
  }
};

const fetchLogs = async () => {
    loading.value = true;
    try {
        logs.value = await api.get('audit-logs/');
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

onMounted(fetchLogs);
</script>
