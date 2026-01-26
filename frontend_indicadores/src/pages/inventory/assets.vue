<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Inventario Global de Activos</h1>
        <p class="text-subtitle-1 text-grey">Gestión de equipos, herramientas y mobiliario institucional</p>
      </v-col>
    </v-row>

    <!-- STATS -->
    <v-row v-if="!loading" class="mb-6">
      <v-col v-for="stat in stats" :key="stat.label" cols="12" md="3">
        <v-card variant="tonal" :color="stat.color" class="rounded-xl pa-4">
          <div class="text-overline">{{ stat.label }}</div>
          <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- FILTERS & ACTIONS -->
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="8">
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Buscar por nombre, código NT o serial..."
          variant="outlined"
          density="compact"
          hide-details
          class="rounded-lg"
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="4" class="text-right">
        <v-btn color="primary" prepend-icon="mdi-plus" size="large" @click="openDialog">
          Registrar Nuevo Activo
        </v-btn>
      </v-col>
    </v-row>

    <!-- INVENTORY TABLE -->
    <v-card elevation="2" class="rounded-xl overflow-hidden">
      <v-data-table
        :headers="headers"
        :items="assets"
        :search="search"
        :loading="loading"
        class="elevation-0"
      >
        <template v-slot:item.internal_code="{ item }">
          <span class="font-weight-bold">{{ item.internal_code }}</span>
        </template>
        <template v-slot:item.category="{ item }">
          <v-chip size="x-small" variant="tonal" color="primary">
            <v-icon start size="x-small">{{ getEquipmentIcon(item.category) }}</v-icon>
            {{ getCategoryLabel(item.category) }}
          </v-chip>
        </template>
        <template v-slot:item.status="{ item }">
          <v-chip size="x-small" :color="getStatusColor(item.status)" class="font-weight-bold">
            {{ getStatusLabel(item.status) }}
          </v-chip>
        </template>
        <template v-slot:item.employee="{ item }">
          <v-btn v-if="item.employee" variant="text" color="primary" size="small" :to="`/employees/${item.employee}`">
             {{ item.employee_name }}
          </v-btn>
          <v-chip v-else size="x-small" color="grey-lighten-1">En Almacén</v-chip>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-history" size="x-small" variant="text" color="primary" title="Historial Técnico" @click="openMaintenance(item)"></v-btn>
          <v-btn icon="mdi-pencil" size="x-small" variant="text" color="info" @click="editItem(item)"></v-btn>
          <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click="deleteItem(item.id)"></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- ASSET DIALOG -->
    <v-dialog v-model="dialog" max-width="600">
      <v-card :title="isEdit ? 'Editar Activo' : 'Registrar Nuevo Activo'" class="rounded-xl">
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="formAsset.internal_code" label="Código NT" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select v-model="formAsset.category" :items="categories" label="Categoría" variant="outlined" required></v-select>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="formAsset.item_name" label="Nombre del Equipo" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formAsset.brand" label="Marca" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formAsset.model" label="Modelo" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formAsset.serial_number" label="S/N (Serial)" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select v-model="formAsset.status" :items="statusOptions" label="Estado" variant="outlined"></v-select>
              </v-col>
              <v-col cols="12">
                <v-autocomplete
                  v-model="formAsset.employee"
                  :items="employees"
                  item-title="full_name"
                  item-value="id"
                  label="Asignar a Empleado (Opcional)"
                  variant="outlined"
                  clearable
                ></v-autocomplete>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="elevated" @click="saveAsset" :loading="saving">Guardar Activo</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- MAINTENANCE LOG DIALOG -->
    <v-dialog v-model="logDialog" max-width="800">
      <v-card v-if="selectedAsset" class="rounded-xl overflow-hidden">
        <v-card-title class="pa-4 bg-secondary text-white d-flex align-center">
            <v-icon class="mr-2">mdi-history</v-icon>
            Historial de Vida Útil: {{ selectedAsset.item_name }} ({{ selectedAsset.internal_code }})
        </v-card-title>
        
        <v-card-text class="pa-0">
            <v-tabs v-model="logTab" color="secondary" grow>
                <v-tab value="history">Historial de Servicios</v-tab>
                <v-tab value="add">Registrar Servicio</v-tab>
            </v-tabs>

            <v-window v-model="logTab">
                <v-window-item value="history" class="pa-4">
                    <v-data-table 
                        :headers="logHeaders" 
                        :items="assetLogs" 
                        :loading="loadingLogs" 
                        density="compact"
                        class="border rounded-lg"
                    >
                        <template v-slot:item.type="{ item }">
                            <v-chip size="x-small" :color="getLogTypeColor(item.type)" variant="outlined">
                                {{ getLogTypeLabel(item.type) }}
                            </v-chip>
                        </template>
                        <template v-slot:item.cost="{ item }">
                            <span class="font-weight-bold text-success">${{ item.cost }}</span>
                        </template>
                    </v-data-table>
                </v-window-item>

                <v-window-item value="add" class="pa-6">
                    <v-form @submit.prevent="saveLog" id="logForm">
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-text-field v-model="formLog.date" label="Fecha del Servicio" type="date" variant="outlined" required></v-text-field>
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-select v-model="formLog.type" :items="logTypes" label="Tipo de Mantenimiento" variant="outlined" required></v-select>
                            </v-col>
                            <v-col cols="12">
                                <v-text-field v-model="formLog.performed_by" label="Técnico / Empresa Responsable" variant="outlined" placeholder="Ej: Soporte IT Interno / Sony Service" required></v-text-field>
                            </v-col>
                            <v-col cols="12">
                                <v-textarea v-model="formLog.description" label="Detalle del Trabajo Realizado" variant="outlined" rows="3" required></v-textarea>
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field v-model="formLog.cost" label="Costo del Servicio ($)" prefix="$" type="number" variant="outlined"></v-text-field>
                            </v-col>
                        </v-row>
                        <div class="d-flex justify-end mt-4">
                            <v-btn color="secondary" type="submit" :loading="savingLog" prepend-icon="mdi-check">Registrar en Bitácora</v-btn>
                        </div>
                    </v-form>
                </v-window-item>
            </v-window>
        </v-card-text>
        <v-card-actions class="pa-4 bg-grey-lighten-4">
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="logDialog = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';

const loading = ref(true);
const saving = ref(false);
const assets = ref([]);
const employees = ref([]);
const search = ref('');
const dialog = ref(false);
const isEdit = ref(false);
const valid = ref(false);

const logDialog = ref(false);
const logTab = ref('history');
const selectedAsset = ref(null);
const assetLogs = ref([]);
const loadingLogs = ref(false);
const savingLog = ref(false);

const formLog = ref({
  date: new Date().toISOString().substr(0, 10),
  type: 'corrective',
  description: '',
  cost: 0,
  performed_by: ''
});

const formAsset = ref({
  internal_code: '',
  item_name: '',
  brand: '',
  model: '',
  category: 'laptop',
  serial_number: '',
  status: 'functional',
  employee: null
});

const headers = [
  { title: 'Código NT', key: 'internal_code' },
  { title: 'Activo', key: 'item_name' },
  { title: 'Marca/Modelo', value: item => `${item.brand || ''} ${item.model || ''}` },
  { title: 'Categoría', key: 'category' },
  { title: 'Responsable', key: 'employee' },
  { title: 'Estado', key: 'status', align: 'center' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' },
];

const categories = [
  {title:'Laptop', value:'laptop'}, 
  {title:'Celular', value:'phone'}, 
  {title:'Herramienta', value:'tool'}, 
  {title:'Mueble', value:'furniture'}, 
  {title:'Uniforme', value:'uniform'}, 
  {title:'Carnet', value:'id_card'}
];

const statusOptions = [
  {title:'Operativo', value:'functional'},
  {title:'Presenta Fallas', value:'failing'},
  {title:'Dañado', value:'broken'},
  {title:'En Taller', value:'maintenance'}
];

const logHeaders = [
  { title: 'Fecha', key: 'date' },
  { title: 'Tipo', key: 'type' },
  { title: 'Descripción', key: 'description' },
  { title: 'Costo', key: 'cost', align: 'end' },
  { title: 'Responsable', key: 'performed_by' },
];

const logTypes = [
  {title:'Preventivo / Rutina', value:'preventive'},
  {title:'Correctivo / Reparación', value:'corrective'},
  {title:'Mejora / Upgrade', value:'upgrade'},
];

const stats = computed(() => [
  { label: 'Total Activos', value: assets.value.length, color: 'primary' },
  { label: 'Asignados', value: assets.value.filter(a => a.employee).length, color: 'success' },
  { label: 'En Almacén', value: assets.value.filter(a => !a.employee).length, color: 'info' },
  { label: 'En Falla', value: assets.value.filter(a => a.status !== 'functional').length, color: 'error' },
]);

const loadData = async () => {
  loading.value = true;
  try {
    const [assetRes, empRes] = await Promise.all([
      api.get('equipment/'),
      api.get('employees/')
    ]);
    assets.value = assetRes;
    employees.value = empRes.map(e => ({ ...e, full_name: `${e.first_name} ${e.last_name}` }));
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const openDialog = () => {
  isEdit.value = false;
  formAsset.value = { internal_code: '', item_name: '', brand: '', model: '', category: 'laptop', serial_number: '', status: 'functional', employee: null };
  dialog.value = true;
};

const editItem = (item) => {
  isEdit.value = true;
  formAsset.value = { ...item };
  dialog.value = true;
};

const openMaintenance = async (item) => {
    selectedAsset.value = item;
    logDialog.value = true;
    logTab.value = 'history';
    loadingLogs.value = true;
    try {
        assetLogs.value = await api.get(`maintenance-logs/?equipment=${item.id}`);
    } catch (e) { console.error(e); }
    finally { loadingLogs.value = false; }
};

const saveLog = async () => {
    savingLog.value = true;
    try {
        await api.post('maintenance-logs/', {
            ...formLog.value,
            equipment: selectedAsset.value.id
        });
        formLog.value = { date: new Date().toISOString().substr(0, 10), type: 'corrective', description: '', cost: 0, performed_by: '' };
        logTab.value = 'history';
        // Reload logs
        assetLogs.value = await api.get(`maintenance-logs/?equipment=${selectedAsset.value.id}`);
        loadData(); // To update states if needed
    } catch (e) {
        alert('Error al registrar mantenimiento');
    } finally {
        savingLog.value = false;
    }
};

const saveAsset = async () => {
  saving.value = true;
  try {
    if (isEdit.value) {
      await api.patch(`equipment/${formAsset.value.id}/`, formAsset.value);
    } else {
      await api.post('equipment/', formAsset.value);
    }
    dialog.value = false;
    loadData();
  } catch (e) {
    alert('Error al guardar el activo');
  } finally {
    saving.value = false;
  }
};

const deleteItem = async (id) => {
  if (confirm('¿Desea dar de baja este activo?')) {
    try {
      await api.delete(`equipment/${id}/`);
      loadData();
    } catch (e) {
      alert('Error al eliminar');
    }
  }
};

// HELPERS
const getEquipmentIcon = (cat) => ({
    laptop: 'mdi-laptop',
    phone: 'mdi-cellphone',
    tool: 'mdi-hammer-wrench',
    furniture: 'mdi-seat-recline-normal',
    uniform: 'mdi-tshirt-crew',
    id_card: 'mdi-card-account-details'
}[cat] || 'mdi-package-variant');

const getStatusColor = (s) => ({
    functional: 'success',
    failing: 'warning',
    broken: 'error',
    maintenance: 'info'
}[s] || 'grey');

const getStatusLabel = (s) => ({
    functional: 'Operativo',
    failing: 'Falla',
    broken: 'Dañado',
    maintenance: 'En Taller'
}[s] || s);

const getLogTypeColor = (t) => ({
    preventive: 'info',
    corrective: 'error',
    upgrade: 'success'
}[t] || 'grey');

const getLogTypeLabel = (t) => logTypes.find(l => l.value === t)?.title || t;

const getCategoryLabel = (c) => categories.find(cat => cat.value === c)?.title || c;

onMounted(loadData);
</script>
