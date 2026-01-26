<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12" class="d-flex justify-space-between align-center">
        <div>
          <h1 class="text-h4 font-weight-bold">Portal de Autogestión</h1>
          <p class="text-subtitle-1 text-grey">Gestiona tus trámites personales de RRHH</p>
        </div>
        <v-btn color="primary" size="large" prepend-icon="mdi-file-plus" @click="dialog = true">
          Nueva Solicitud
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card class="rounded-xl elevation-3">
          <v-card-title class="pa-4 bg-primary text-white">Mis Solicitudes Recientes</v-card-title>
          <v-data-table
            :headers="headers"
            :items="requests"
            :loading="loading"
            class="elevation-0"
          >
            <template v-slot:item.type="{ item }">
              {{ typeLabels[item.type] }}
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="statusColors[item.status]" size="small" class="text-uppercase font-weight-bold">
                {{ statusLabels[item.status] }}
              </v-chip>
            </template>
            <template v-slot:item.created_at="{ item }">
              {{ new Date(item.created_at).toLocaleDateString() }}
            </template>
          </v-data-table>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="rounded-xl elevation-3 mb-4" color="info" variant="tonal">
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-information-outline</v-icon>
              <div>
                <div class="text-h6 font-weight-bold">Flujo de Aprobación</div>
                <div class="text-body-2">Toda solicitud es enviada automáticamente a tu supervisor directo para su revisión.</div>
              </div>
            </div>
          </v-card-text>
        </v-card>

        <v-card v-if="employee" class="rounded-xl elevation-3 pa-4">
          <div class="text-center">
            <v-avatar size="100" color="primary" class="mb-4">
              <v-icon size="60" color="white">mdi-account</v-icon>
            </v-avatar>
            <h2 class="text-h5 font-weight-bold">{{ employee.first_name }} {{ employee.last_name }}</h2>
            <p class="text-grey">{{ employee.position }}</p>
            <v-divider class="my-4"></v-divider>
            <div class="text-left">
              <div class="d-flex justify-space-between mb-2">
                <span>Departamento:</span>
                <span class="font-weight-bold">{{ employee.department_detail?.name || 'Vínculo no establecido' }}</span>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Supervisor:</span>
                <span class="font-weight-bold">{{ employee.supervisor_name || 'Sin asignar' }}</span>
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- NEW REQUEST DIALOG -->
    <v-dialog v-model="dialog" max-width="600" persistent>
      <v-card class="rounded-xl overflow-hidden">
        <v-card-title class="pa-4 bg-primary text-white d-flex justify-space-between align-center">
          <span>Nueva Solicitud de Trámite</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="dialog = false"></v-btn>
        </v-card-title>
        <v-card-text class="pa-6">
          <v-form @submit.prevent="submitRequest" id="requestForm">
            <v-select
              v-model="form.type"
              :items="requestTypeItems"
              label="¿Qué necesitas solicitar?"
              variant="outlined"
              required
            ></v-select>

            <v-row v-if="form.type === 'vacation'">
              <v-col cols="12" md="6">
                <v-text-field v-model="form.start_date" label="Desde" type="date" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.end_date" label="Hasta" type="date" variant="outlined"></v-text-field>
              </v-col>
            </v-row>

            <v-textarea
              v-model="form.reason"
              label="Justificación / Motivo de la solicitud"
              variant="outlined"
              rows="4"
              counter
              required
            ></v-textarea>
            
            <button type="submit" style="display:none"></button>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" size="large" type="submit" form="requestForm" :loading="saving" prepend-icon="mdi-send">
            Enviar Solicitud
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const employee = ref(null);
const requests = ref([]);
const loading = ref(true);
const dialog = ref(false);
const saving = ref(false);

const headers = [
  { title: 'Fecha', key: 'created_at' },
  { title: 'Trámite', key: 'type' },
  { title: 'Estado', key: 'status' },
  { title: 'Comentario Jefe', key: 'supervisor_comment' },
];

const typeLabels = { vacation: 'Vacaciones', benefits: 'Prestaciones', certificate: 'Constancia', loan: 'Préstamo', other: 'Otro' };
const statusLabels = { pending: 'Pendiente', approved: 'Aprobado', rejected: 'Rechazado' };
const statusColors = { pending: 'warning', approved: 'success', rejected: 'error' };

const requestTypeItems = Object.entries(typeLabels).map(([value, title]) => ({ value, title }));

const form = ref({
  type: 'vacation',
  reason: '',
  start_date: null,
  end_date: null
});

const loadInitial = async () => {
  loading.value = true;
  try {
    const [empRes, reqRes] = await Promise.all([
      api.get('employees/me/'),
      api.get('hr-requests/')
    ]);
    employee.value = empRes;
    requests.value = reqRes;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const submitRequest = async () => {
  if (!form.value.reason) return;
  
  saving.value = true;
  try {
    await api.post('hr-requests/', form.value);
    dialog.value = false;
    form.value = { type: 'vacation', reason: '', start_date: null, end_date: null };
    loadInitial();
  } catch (e) {
    alert('Error al enviar solicitud');
  } finally {
    saving.value = false;
  }
};

onMounted(loadInitial);
</script>
