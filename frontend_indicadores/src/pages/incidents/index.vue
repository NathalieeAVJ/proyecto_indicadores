<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12" md="8" class="d-flex align-center">
        <v-text-field v-model="startDate" type="date" label="Desde" hide-details class="mr-2" density="compact" @change="fetchIncidents"></v-text-field>
        <v-text-field v-model="endDate" type="date" label="Hasta" hide-details class="mr-2" density="compact" @change="fetchIncidents"></v-text-field>
        <v-btn icon="mdi-refresh" @click="fetchIncidents" variant="text"></v-btn>
      </v-col>
      <v-col cols="12" md="4" class="text-right d-flex align-center justify-end">
        <v-btn color="error" prepend-icon="mdi-file-pdf-box" @click="exportPDF" variant="tonal" class="mr-2">PDF</v-btn>
        <v-btn color="primary" @click="openDialog()" prepend-icon="mdi-plus">Nueva Incidencia</v-btn>
      </v-col>
    </v-row>

    <v-card elevation="2">
      <v-data-table
        :headers="headers"
        :items="incidents"
        :loading="loadingTable"
        class="elevation-0"
      >
        <template v-slot:item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small">
            {{ getStatusLabel(item.status) }}
          </v-chip>
        </template>
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" variant="text" color="primary" @click="openDialog(item)" title="Editar / Resolver">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn icon size="small" variant="text" color="secondary" @click="createOT(item)" title="Generar Orden de Trabajo">
            <v-icon>mdi-clipboard-plus</v-icon>
          </v-btn>
          <v-btn icon size="small" variant="text" color="error" @click="deleteItem(item)" title="Eliminar">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- CRUD DIALOG -->
    <v-dialog v-model="dialog" max-width="800" persistent>
      <v-card>
        <v-card-title class="pa-4 text-h5 d-flex justify-space-between align-center">
          <span>{{ isEdit ? `Incidencia #${editedId}` : 'Reportar Incidencia' }}</span>
          <v-btn icon variant="text" @click="dialog = false"><v-icon>mdi-close</v-icon></v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-form @submit.prevent="saveItem" ref="formRef">
            <v-text-field v-model="form.title" label="Asunto / Título de la Falla" required :rules="[v => !!v || 'Requerido']"></v-text-field>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-autocomplete
                  v-model="form.phone_number"
                  :items="phones"
                  item-title="number"
                  item-value="id"
                  label="Número Telefónico Afectado"
                  required
                  :rules="[v => !!v || 'Requerido']"
                ></v-autocomplete>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.failure_type"
                  :items="failureTypes"
                  item-title="name"
                  item-value="id"
                  label="Tipo de Falla"
                  required
                  :rules="[v => !!v || 'Requerido']"
                ></v-select>
              </v-col>
            </v-row>

            <v-textarea v-model="form.description" label="Descripción detallada de la falla" rows="2"></v-textarea>

            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.status"
                  :items="statuses"
                  item-title="title"
                  item-value="value"
                  label="Estado Actual"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-autocomplete
                  v-model="form.assigned_to"
                  :items="users"
                  item-title="username"
                  item-value="id"
                  label="Asignar a Técnico"
                  clearable
                ></v-autocomplete>
              </v-col>
            </v-row>

            <v-expand-transition>
              <div v-if="form.status === 'solved'">
                <v-divider class="my-4"></v-divider>
                <h3 class="text-subtitle-1 font-weight-bold mb-3">Detalles de la Solución</h3>
                
                <v-textarea v-model="form.solution_comment" label="Comentarios de Solución" rows="2"></v-textarea>
                <v-text-field v-model="form.solved_date" type="datetime-local" label="Fecha y Hora de Solución"></v-text-field>

                <!-- REPUESTOS USADOS -->
                <v-card variant="outlined" class="mt-4">
                  <v-card-title class="text-subtitle-2 pa-2 bg-grey-lighten-4">
                    <v-icon size="small" class="me-2">mdi-package-variant</v-icon>
                    Repuestos Utilizados
                  </v-card-title>
                  <v-card-text class="pa-2">
                    <v-row v-for="(item, index) in usedParts" :key="index" class="mb-0 align-center" dense>
                      <v-col cols="7">
                        <v-autocomplete
                          v-model="item.spare_part"
                          :items="spareParts"
                          item-title="name"
                          item-value="id"
                          label="Repuesto"
                          density="compact"
                          hide-details
                        ></v-autocomplete>
                      </v-col>
                      <v-col cols="3">
                        <v-text-field
                          v-model.number="item.quantity_used"
                          label="Cant."
                          type="number"
                          min="1"
                          density="compact"
                          hide-details
                        ></v-text-field>
                      </v-col>
                      <v-col cols="2" class="text-right">
                        <v-btn icon color="error" variant="text" size="small" @click="usedParts.splice(index, 1)">
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </v-col>
                    </v-row>
                    <v-btn variant="text" size="small" color="primary" @click="usedParts.push({spare_part: null, quantity_used: 1})" class="mt-2">
                      <v-icon start>mdi-plus</v-icon> Agregar Repuesto
                    </v-btn>
                  </v-card-text>
                </v-card>
              </div>
            </v-expand-transition>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="saveItem" :loading="saving">
            {{ isEdit ? 'Actualizar' : 'Reportar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { formatDate } from '@/utils/format';
import { generatePDFReport } from '@/utils/reports';

const authStore = useAuthStore();
const incidents = ref([]);
const phones = ref([]);
const failureTypes = ref([]);
const users = ref([]);
const spareParts = ref([]);
const usedParts = ref([]);

const loadingTable = ref(true);
const dialog = ref(false);
const saving = ref(false);
const isEdit = ref(false);
const editedId = ref(null);
const formRef = ref(null);
const originalStatus = ref('');

const startDate = ref('');
const endDate = ref('');

const form = ref({
  title: '', phone_number: null, failure_type: null, description: '',
  status: 'pending', assigned_to: null, solution_comment: '', solved_date: ''
});

const statuses = [
  { title: 'Pendiente', value: 'pending' },
  { title: 'En Revisión', value: 'in_review' },
  { title: 'Solucionada', value: 'solved' },
  { title: 'Pospuesta', value: 'postponed' },
];

const headers = [
  { title: 'ID', key: 'id', width: '70px' },
  { title: 'Asunto', key: 'title' },
  { title: 'Número', key: 'phone_number_detail.number' },
  { title: 'Tipo Falla', key: 'failure_type_detail.name' },
  { title: 'Estado', key: 'status', align: 'center' },
  { title: 'Fecha', key: 'created_at' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const getStatusColor = (s) => {
  const map = { pending: 'error', in_review: 'warning', solved: 'success', postponed: 'grey' };
  return map[s] || 'grey';
};

const getStatusLabel = (s) => statuses.find(x => x.value === s)?.title.toUpperCase() || s;

const fetchIncidents = async () => {
  loadingTable.value = true;
  try {
    const params = new URLSearchParams();
    if (startDate.value) params.append('start', startDate.value);
    if (endDate.value) params.append('end', endDate.value);
    incidents.value = await api.get(`incidents/?${params.toString()}`);
  } catch (e) { console.error(e); }
  finally { loadingTable.value = false; }
};

const loadMetadata = async () => {
  try {
    const [p, f, u, sp] = await Promise.all([
      api.get('phones/'), api.get('failure-types/'), api.get('users/'), api.get('spare-parts/')
    ]);
    phones.value = p; failureTypes.value = f; users.value = u; spareParts.value = sp;
  } catch (e) { console.error(e); }
};

const openDialog = (item = null) => {
  usedParts.value = [];
  if (item) {
    isEdit.value = true;
    editedId.value = item.id;
    originalStatus.value = item.status;
    form.value = { ...item };
    if (form.value.solved_date) form.value.solved_date = form.value.solved_date.slice(0, 16);
  } else {
    isEdit.value = false;
    editedId.value = null;
    originalStatus.value = '';
    form.value = { title: '', phone_number: null, failure_type: null, description: '', status: 'pending', assigned_to: null, solution_comment: '', solved_date: '' };
  }
  dialog.value = true;
};

const saveItem = async () => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;

  saving.value = true;
  try {
    if (isEdit.value) {
      await api.patch(`incidents/${editedId.value}/`, form.value);
      // Registrar repuestos solo si se cambia a SOLVED ahora
      if (form.value.status === 'solved' && originalStatus.value !== 'solved') {
        for (const up of usedParts.value) {
          if (up.spare_part) {
            await api.post('spare-part-usage/', { ...up, incident_type: 'phone', incident_id: editedId.value });
          }
        }
      }
    } else {
      await api.post('incidents/', form.value);
    }
    dialog.value = false;
    fetchIncidents();
  } catch (e) {
    console.error(e);
    alert('Error al guardar: ' + (e.data?.detail || e.message));
  } finally { saving.value = false; }
};

const deleteItem = async (item) => {
  if (confirm(`¿Eliminar incidencia #${item.id}?`)) {
    await api.delete(`incidents/${item.id}/`);
    fetchIncidents();
  }
};

const createOT = async (item) => {
  try {
    await api.post('work-orders/', { incident_type: 'phone', incident_id: item.id, assigned_to: item.assigned_to || authStore.user.id, status: 'assigned' });
    alert('Orden de Trabajo generada');
  } catch (e) { alert('Error al generar OT'); }
};

const exportPDF = async () => {
  const reportHeaders = ['ID', 'Asunto', 'Teléfono', 'Tipo Falla', 'Estado', 'Fecha'];
  const body = incidents.value.map(i => [i.id, i.title, i.phone_number_detail?.number, i.failure_type_detail?.name, i.status.toUpperCase(), formatDate(i.created_at)]);
  await generatePDFReport({ title: 'Reporte de Incidencias Telefónicas', headers: reportHeaders, body });
};

onMounted(() => {
  fetchIncidents();
  loadMetadata();
});
</script>
