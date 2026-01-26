<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Control de Aprobaciones</h1>
        <p class="text-subtitle-1 text-grey">Gestión de trámites y solicitudes de tu personal subordinado</p>
      </v-col>
    </v-row>

    <v-row v-if="pendingRequests.length > 0">
      <v-col cols="12">
        <v-alert
          type="info"
          variant="tonal"
          title="Solicitudes Pendientes"
          class="mb-6 rounded-xl border-info border-sm"
          prepend-icon="mdi-human-greeting-proximity"
        >
          Tienes {{ pendingRequests.length }} trámites esperando por tu revisión.
        </v-alert>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="rounded-xl">
          <v-tabs v-model="tab" bg-color="primary" class="rounded-t-xl">
            <v-tab value="pending">Pendientes</v-tab>
            <v-tab value="history">Historial Global</v-tab>
          </v-tabs>

          <v-card-text class="pa-0">
            <v-window v-model="tab">
              <!-- PENDING TAB -->
              <v-window-item value="pending">
                <v-data-table
                  :headers="headers"
                  :items="pendingRequests"
                  :loading="loading"
                  class="elevation-0"
                >
                  <template v-slot:item.type="{ item }">{{ typeLabels[item.type] }}</template>
                  <template v-slot:item.created_at="{ item }">{{ new Date(item.created_at).toLocaleDateString() }}</template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn color="success" size="small" class="mr-2" @click="openActionDialog(item, 'approve')">Aprobar</v-btn>
                    <v-btn color="error" size="small" variant="outlined" @click="openActionDialog(item, 'reject')">Rechazar</v-btn>
                  </template>
                </v-data-table>
              </v-window-item>

              <!-- HISTORY TAB -->
              <v-window-item value="history">
                <v-data-table
                  :headers="headersHistory"
                  :items="allRequests"
                  :loading="loading"
                  class="elevation-0"
                >
                  <template v-slot:item.type="{ item }">{{ typeLabels[item.type] }}</template>
                  <template v-slot:item.status="{ item }">
                    <v-chip :color="statusColors[item.status]" size="x-small" class="font-weight-bold">
                      {{ statusLabels[item.status] }}
                    </v-chip>
                  </template>
                </v-data-table>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- ACTION DIALOG -->
    <v-dialog v-model="actionDialog" max-width="500">
      <v-card v-if="selectedReq" class="rounded-xl">
        <v-card-title class="pa-4" :class="actionType === 'approve' ? 'bg-success' : 'bg-error'">
          <span class="text-white">{{ actionType === 'approve' ? 'Aprobar Solicitud' : 'Rechazar Solicitud' }}</span>
        </v-card-title>
        <v-card-text class="pa-6">
          <p class="mb-4">
            <strong>Solicitante:</strong> {{ selectedReq.employee_name }}<br>
            <strong>Trámite:</strong> {{ typeLabels[selectedReq.type] }}<br>
            <strong>Motivo:</strong> {{ selectedReq.reason }}
          </p>
          <v-textarea
            v-model="actionComment"
            label="Comentarios / Observaciones"
            rows="3"
            variant="outlined"
            placeholder="Escribe el motivo de la decisión aquí..."
          ></v-textarea>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="actionDialog = false">Cancelar</v-btn>
          <v-btn :color="actionType === 'approve' ? 'success' : 'error'" @click="processRequest" :loading="processing">
            Confirmar {{ actionType === 'approve' ? 'Aprobación' : 'Rechazo' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';

const requests = ref([]);
const loading = ref(true);
const tab = ref('pending');

const actionDialog = ref(false);
const actionType = ref('');
const selectedReq = ref(null);
const actionComment = ref('');
const processing = ref(false);

const typeLabels = { vacation: 'Vacaciones', benefits: 'Prestaciones', certificate: 'Constancia', loan: 'Préstamo', other: 'Otro' };
const statusLabels = { pending: 'Pendiente', approved: 'Aprobado', rejected: 'Rechazado' };
const statusColors = { pending: 'warning', approved: 'success', rejected: 'error' };

const headers = [
  { title: 'Fecha', key: 'created_at' },
  { title: 'Empleado', key: 'employee_name' },
  { title: 'Trámite', key: 'type' },
  { title: 'Justificación', key: 'reason' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const headersHistory = [
  { title: 'Fecha', key: 'created_at' },
  { title: 'Empleado', key: 'employee_name' },
  { title: 'Trámite', key: 'type' },
  { title: 'Estado', key: 'status' },
  { title: 'Resuelto por', key: 'resolved_by_name' },
];

const pendingRequests = computed(() => requests.value.filter(r => r.status === 'pending'));
const allRequests = computed(() => requests.value);

const loadRequests = async () => {
  loading.value = true;
  try {
    requests.value = await api.get('hr-requests/');
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const openActionDialog = (req, type) => {
  selectedReq.value = req;
  actionType.value = type;
  actionComment.value = type === 'approve' ? 'Aprobado.' : 'Rechazado.';
  actionDialog.value = true;
};

const processRequest = async () => {
  processing.value = true;
  try {
    const endpoint = `hr-requests/${selectedReq.value.id}/${actionType.value}/`;
    await api.post(endpoint, { comment: actionComment.value });
    actionDialog.value = false;
    loadRequests();
  } catch (e) {
    alert('Error al procesar solicitud');
  } finally {
    processing.value = false;
  }
};

onMounted(loadRequests);
</script>
