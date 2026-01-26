<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Lista Negra / Personal Egresado</h1>
        <p class="text-subtitle-1 text-grey">Control de personal desincorporado y gestión de antecedentes laborales</p>
      </v-col>
    </v-row>

    <!-- STATS -->
    <v-row v-if="!loading" class="mb-6">
      <v-col cols="12" md="4">
        <v-card variant="tonal" color="error" class="rounded-xl pa-4">
          <div class="text-overline">Total en Lista Negra</div>
          <div class="text-h4 font-weight-bold">{{ items.length }}</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- DATA TABLE -->
    <v-card elevation="2" class="rounded-xl overflow-hidden">
      <v-row class="pa-4 pt-6 align-center">
        <v-col cols="12" md="6">
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            label="Buscar por nombre, Cédula o motivo..."
            variant="outlined"
            density="compact"
            hide-details
          ></v-text-field>
        </v-col>
      </v-row>

      <v-data-table
        :headers="headers"
        :items="items"
        :search="search"
        :loading="loading"
        class="elevation-0"
      >
        <template v-slot:item.name="{ item }">
          <div class="font-weight-bold text-error">{{ item.first_name }} {{ item.last_name }}</div>
          <div class="text-caption text-grey">{{ item.dni }}</div>
        </template>
        
        <template v-slot:item.blacklist_date="{ item }">
          {{ formatDate(item.blacklist_date) }}
        </template>

        <template v-slot:item.blacklist_reason="{ item }">
          <div class="text-truncate" style="max-width: 300px;" :title="item.blacklist_reason">
            {{ item.blacklist_reason || 'No especificado' }}
          </div>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn
            color="success"
            prepend-icon="mdi-account-plus"
            size="small"
            variant="tonal"
            @click="openReactivate(item)"
          >
            Re-contratar
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- REACTIVATE DIALOG -->
    <v-dialog v-model="dialog" max-width="500">
      <v-card class="rounded-xl">
        <v-card-title class="pa-4 bg-success text-white">
            Confirmar Reincorporación
        </v-card-title>
        <v-card-text class="pa-6">
            <p>¿Está seguro de que desea reintroducir a <strong>{{ selected?.first_name }} {{ selected?.last_name }}</strong> a la nómina de activos?</p>
            <p class="text-caption text-grey mt-2">
                * El estado pasará a "Activo".<br>
                * El acceso al sistema (usuario) deberá ser reactivado manualmente por seguridad.
            </p>
        </v-card-text>
        <v-card-actions class="pa-4 px-6">
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
            <v-btn color="success" variant="elevated" @click="confirmReactivate" :loading="saving">Reactivar Empleado</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { formatDate } from '@/utils/format';

const loading = ref(true);
const saving = ref(false);
const items = ref([]);
const search = ref('');
const dialog = ref(false);
const selected = ref(null);

const headers = [
  { title: 'Empleado', key: 'name' },
  { title: 'Último Cargo', key: 'position' },
  { title: 'Fecha Egreso', key: 'blacklist_date' },
  { title: 'Motivo de Salida', key: 'blacklist_reason' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' }
];

const loadData = async () => {
  loading.value = true;
  try {
    // Pedimos específicamente los de lista negra
    items.value = await api.get('employees/?status=blacklisted');
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const openReactivate = (item) => {
    selected.value = item;
    dialog.value = true;
};

const confirmReactivate = async () => {
    saving.value = true;
    try {
        await api.post(`employees/${selected.value.id}/reactivate/`);
        dialog.value = false;
        loadData();
    } catch (e) {
        alert('Error al reactivar');
    } finally {
        saving.value = false;
    }
};

onMounted(loadData);
</script>
