<template>
  <v-container>
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Auditoría de Sistema</h1>
        <v-btn icon="mdi-refresh" @click="fetchLogs" :loading="loading" variant="text"></v-btn>
      </v-col>
    </v-row>

    <!-- FILTERS -->
    <v-card class="mb-4 elevation-1">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedModule"
              :items="moduleOptions"
              label="Filtrar por Módulo"
              clearable
              hide-details
              @update:model-value="fetchLogs"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Buscador libre..."
              clearable
              hide-details
              density="compact"
              variant="solo-filled"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3" class="text-right">
             <v-btn color="primary" block @click="fetchLogs">Recargar API</v-btn>
          </v-col>
          <v-col cols="12" md="2" class="text-right">
             <v-btn variant="text" block @click="resetFilters">Limpiar</v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-data-table
            :headers="headers"
            :items="logs"
            :loading="loading"
            :search="search"
            class="elevation-0"
          >
            <template v-slot:item.action="{ item }">
              <v-chip :color="getActionColor(item.action)" size="small">
                {{ getActionLabel(item.action) }}
              </v-chip>
            </template>
            <template v-slot:item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>
            <template v-slot:item.module="{ item }">
               <v-chip size="x-small" variant="outlined" :color="getModuleColor(item.module)">{{ item.module.toUpperCase() }}</v-chip>
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
const selectedModule = ref(null);
const search = ref('');

const moduleOptions = [
    { title: 'Empleados', value: 'employees' },
    { title: 'Usuarios', value: 'users' },
    { title: 'Teléfonos', value: 'phones' },
    { title: 'Radiobases', value: 'radio-bases' },
    { title: 'Incidencias', value: 'incidents' },
    { title: 'Tickets RB', value: 'rb-incidents' },
    { title: 'Repuestos', value: 'spare-parts' },
    { title: 'Presupuestos', value: 'budgets' },
];

const headers = [
  { title: 'Fecha', key: 'created_at', width: '180px' },
  { title: 'Usuario', key: 'username' },
  { title: 'Acción', key: 'action', align: 'center' },
  { title: 'Módulo', key: 'module', align: 'center' },
  { title: 'ID Obj', key: 'object_id', align: 'center' },
  { title: 'Descripción', key: 'description' },
  { title: 'IP', key: 'ip_address' },
];

const getActionColor = (a) => {
  const colors = { create: 'success', update: 'info', delete: 'error', login: 'warning' };
  return colors[a] || 'grey';
};

const getActionLabel = (a) => {
  const labels = { create: 'CREACIÓN', update: 'ACTUALIZACIÓN', delete: 'ELIMINACIÓN', login: 'INICIO SESIÓN' };
  return labels[a] || (a || '').toUpperCase();
};

const getModuleColor = (m) => {
    if (m === 'employees') return 'primary';
    if (m === 'users') return 'secondary';
    if (m?.includes('incidents')) return 'error';
    return 'grey';
};

const fetchLogs = async () => {
    loading.value = true;
    try {
        const params = new URLSearchParams();
        if (selectedModule.value) params.append('module', selectedModule.value);
        
        logs.value = await api.get(`audit-logs/?${params.toString()}`);
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

const resetFilters = () => {
    selectedModule.value = null;
    search.value = '';
    fetchLogs();
};

onMounted(fetchLogs);
</script>
