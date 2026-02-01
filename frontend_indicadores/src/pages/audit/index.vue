<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Bitácora de Auditoría</h1>
        <p class="text-subtitle-1">Registro de actividad y seguridad del sistema</p>
      </v-col>
    </v-row>

    <v-card elevation="2">
      <v-card-title class="d-flex align-center py-3">
        <v-icon icon="mdi-shield-search" class="mr-2"></v-icon>
        Registros
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-inner-icon="mdi-magnify"
          label="Buscar (Usuario, Acción, IP...)"
          single-line
          hide-details
          density="compact"
          class="mr-4"
          style="max-width: 300px"
        ></v-text-field>
        <v-btn icon="mdi-refresh" variant="text" @click="fetchLogs" :loading="loading"></v-btn>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="logs"
        :loading="loading"
        :search="search"
        class="elevation-0"
        hover
        density="compact"
      >
        <!-- Action Column Coloring -->
        <template v-slot:item.action="{ item }">
          <v-chip :color="getActionColor(item.action)" size="small" class="text-uppercase font-weight-bold">
            {{ item.action }}
          </v-chip>
        </template>

        <!-- Date Formatting -->
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <!-- User/IP formatting -->
         <template v-slot:item.username="{ item }">
            <div class="font-weight-medium">{{ item.username }}</div>
            <div class="text-caption text-medium-emphasis">{{ item.ip_address }}</div>
        </template>

        <template v-slot:no-data>
          <div class="pa-4 text-center">No hay registros de auditoría disponibles</div>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const logs = ref([]);
const loading = ref(false);
const search = ref('');

const headers = [
  { title: 'Fecha/Hora', key: 'created_at', width: '180px' },
  { title: 'Usuario / IP', key: 'username' },
  { title: 'Módulo', key: 'module' },
  { title: 'Acción', key: 'action' },
  { title: 'Descripción', key: 'description' },
];

const getActionColor = (action) => {
  if (!action) return 'grey';
  const a = action.toLowerCase();
  if (a.includes('create') || a.includes('add') || a === 'post') return 'success';
  if (a.includes('update') || a.includes('edit') || a === 'put' || a === 'patch') return 'info';
  if (a.includes('delete') || a.includes('remove') || a === 'delete') return 'error';
  if (a.includes('login')) return 'primary';
  return 'grey';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString();
};

const fetchLogs = async () => {
  loading.value = true;
  try {
    // Assuming API returns a list. If paginated via 'results', we might need response.data.results
    const response = await api.get('audit-logs/');
    logs.value = Array.isArray(response) ? response : (response.results || []);
  } catch (error) {
    console.error('Error fetching audit logs:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchLogs();
});
</script>
