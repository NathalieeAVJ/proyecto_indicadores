<template>
  <v-container>
    <v-row>
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Órdenes de Trabajo</h1>
        <div class="d-flex align-center">
          <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" label="Buscar OT..." hide-details density="compact" variant="solo-filled" class="mr-4" style="width: 300px;"></v-text-field>
          <v-btn color="error" prepend-icon="mdi-file-pdf-box" @click="exportWorkOrdersReport" variant="tonal">Reporte PDF</v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-data-table
            :headers="headers"
            :items="orders"
            :loading="loading"
            :search="search"
            class="elevation-0"
          >
            <template v-slot:item.incident_type="{ item }">
              {{ item.incident_type === 'phone' ? 'TELEFONÍA' : 'RADIOBASE' }}
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="getStatusColor(item.status)" size="small">
                {{ getStatusLabel(item.status) }}
              </v-chip>
            </template>
            <template v-slot:item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn icon="mdi-eye" size="x-small" color="primary" variant="text" @click="viewOrder(item)"></v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- View/Edit Order Dialog -->
    <v-dialog v-model="showDialog" max-width="700px">
        <v-card v-if="selectedOrder" title="Detalle de OT">
            <v-form @submit.prevent="saveOrder" id="otForm">
                <v-card-text>
                    <v-row>
                        <v-col cols="12"><h3 class="text-subtitle-1 mb-2">Checklist de Verificación</h3></v-col>
                        <v-col cols="12" md="4">
                            <v-checkbox v-model="selectedOrder.checked_power" label="Energía Verificada"></v-checkbox>
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-checkbox v-model="selectedOrder.checked_wiring" label="Cableado OK"></v-checkbox>
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-checkbox v-model="selectedOrder.checked_config" label="Software/Config OK"></v-checkbox>
                        </v-col>
                        
                        <v-col cols="12">
                            <v-select v-model="selectedOrder.status" :items="statuses" label="Estado de la Orden"></v-select>
                        </v-col>
                        
                        <v-col cols="12">
                            <v-textarea v-model="selectedOrder.technician_notes" label="Notas Técnicas de Campo" rows="3"></v-textarea>
                        </v-col>
                    </v-row>
                    <button type="submit" style="display:none"></button>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn @click="showDialog = false">Cerrar</v-btn>
                    <v-btn color="primary" type="submit" form="otForm" :loading="saving">Guardar Avances</v-btn>
                </v-card-actions>
            </v-form>
        </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { generatePDFReport } from '@/utils/reports';
import { formatDate } from '@/utils/format';

const authStore = useAuthStore();

const orders = ref([]);
const search = ref('');
const loading = ref(true);
const saving = ref(false);
const showDialog = ref(false);
const selectedOrder = ref(null);

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Tipo', key: 'incident_type' },
  { title: 'Incidente #', key: 'incident_id' },
  { title: 'Estado', key: 'status' },
  { title: 'Fecha', key: 'created_at' },
  { title: 'Acciones', key: 'actions', sortable: false },
];

const statuses = [
    { title: 'Asignada', value: 'assigned' },
    { title: 'En Proceso', value: 'in_progress' },
    { title: 'En Pruebas', value: 'testing' },
    { title: 'Completada', value: 'completed' }
];

const getStatusColor = (s) => {
  if (s === 'completed') return 'success';
  if (s === 'in_progress') return 'info';
  return 'warning';
};

const getStatusLabel = (s) => {
  switch(s) {
    case 'assigned': return 'ASIGNADA';
    case 'in_progress': return 'EN PROCESO';
    case 'testing': return 'EN PRUEBAS';
    case 'completed': return 'COMPLETADA';
    default: return (s || '').toUpperCase();
  }
};

const fetchOrders = async () => {
    loading.value = true;
    try {
        orders.value = await api.get('work-orders/');
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

const viewOrder = (order) => {
    selectedOrder.value = { ...order };
    showDialog.value = true;
};

const saveOrder = async () => {
    saving.value = true;
    try {
        await api.patch(`work-orders/${selectedOrder.value.id}/`, selectedOrder.value);
        showDialog.value = false;
        fetchOrders();
    } catch (e) {
        console.error(e);
    } finally {
        saving.value = false;
    }
};

const exportWorkOrdersReport = async () => {
    const headers = ['ID', 'Tipo', 'Incidente #', 'Estado', 'Fecha'];
    const body = orders.value.map(o => [
        o.id,
        o.incident_type === 'phone' ? 'TELEFONIA' : 'RADIOBASE',
        o.incident_id,
        o.status.toUpperCase(),
        formatDate(o.created_at)
    ]);

    await generatePDFReport({
        title: 'Reporte de Servicios de Campo (OT)',
        subtitle: 'Actividades de Mantenimiento y Resolución - Caracas',
        headers: headers,
        body: body,
        filename: `Reporte_OT_NatTelf_${Date.now()}.pdf`,
        author: authStore.user?.username || 'Sistema NatTelf',
        metadata: {
            'Área': 'Field Service / Mantenimiento',
            'Región': 'Distrito Capital',
            'Total OTs': body.length
        }
    });
};

onMounted(fetchOrders);
</script>
