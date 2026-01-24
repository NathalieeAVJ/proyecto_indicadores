<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn variant="text" to="/budgets" class="mb-4">
          <v-icon start>mdi-arrow-left</v-icon>
          Volver a Presupuestos
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-if="budget">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Presupuesto #{{ budget.id }}</span>
            <v-chip :color="getStatusColor(budget.status)">
              {{ budget.status_display }}
            </v-chip>
          </v-card-title>
          <v-card-subtitle>{{ budget.title }}</v-card-subtitle>
          <v-card-text>
            <div class="text-body-2 text-medium-emphasis">Descripción / Justificación</div>
            <div class="mb-4">{{ budget.description }}</div>

            <v-row class="mb-4">
              <v-col cols="6" md="3">
                <div class="text-body-2 text-medium-emphasis">Solicitado por</div>
                <div>{{ budget.requested_by_detail?.username }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-body-2 text-medium-emphasis">Fecha</div>
                <div>{{ formatDate(budget.created_at) }}</div>
              </v-col>
              <v-col cols="6" md="3" v-if="budget.approved_by_detail">
                <div class="text-body-2 text-medium-emphasis">Aprobado por</div>
                <div>{{ budget.approved_by_detail?.username }}</div>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>
            <h3 class="text-h6 mb-3">Ítems del Presupuesto</h3>

            <v-table>
              <thead>
                <tr>
                  <th>Repuesto</th>
                  <th class="text-center">Cantidad</th>
                  <th class="text-end">Precio Unit.</th>
                  <th class="text-end">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in budget.items" :key="item.id">
                  <td>{{ item.spare_part_detail?.name }}</td>
                  <td class="text-center">{{ item.quantity }}</td>
                  <td class="text-end">${{ formatNumber(item.unit_price) }}</td>
                  <td class="text-end">${{ formatNumber(item.subtotal) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <th colspan="3" class="text-end">Total:</th>
                  <th class="text-end">${{ formatNumber(budget.requested_amount) }}</th>
                </tr>
                <tr v-if="budget.approved_amount">
                  <th colspan="3" class="text-end text-success">Monto Aprobado:</th>
                  <th class="text-end text-success">${{ formatNumber(budget.approved_amount) }}</th>
                </tr>
              </tfoot>
            </v-table>

            <div v-if="budget.approval_notes" class="mt-4">
              <div class="text-body-2 text-medium-emphasis">Notas de Aprobación</div>
              <div>{{ budget.approval_notes }}</div>
            </div>
          </v-card-text>
          <v-card-actions v-if="canPerformActions">
            <v-btn color="warning" @click="submitBudget" v-if="budget.status === 'draft'" :loading="actionLoading">
              <v-icon start>mdi-send</v-icon>
              Enviar para Aprobación
            </v-btn>
            <v-btn color="success" @click="openApproveDialog" v-if="budget.status === 'pending' && isAdmin">
              <v-icon start>mdi-check</v-icon>
              Aprobar
            </v-btn>
            <v-btn color="error" @click="openRejectDialog" v-if="budget.status === 'pending' && isAdmin">
              <v-icon start>mdi-close</v-icon>
              Rechazar
            </v-btn>
            <v-btn color="info" @click="executeBudget" v-if="budget.status === 'approved'" :loading="actionLoading">
              <v-icon start>mdi-play</v-icon>
              Ejecutar (Agregar al Inventario)
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Approve Dialog -->
    <v-dialog v-model="approveDialog" max-width="500">
      <v-card>
        <v-card-title>Aprobar Presupuesto</v-card-title>
        <v-card-text>
          <v-text-field
            v-model.number="approveData.approved_amount"
            label="Monto Aprobado"
            type="number"
            prefix="$"
          ></v-text-field>
          <v-textarea
            v-model="approveData.approval_notes"
            label="Notas de Aprobación"
            rows="2"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="approveDialog = false">Cancelar</v-btn>
          <v-btn color="success" @click="approveBudget" :loading="actionLoading">Aprobar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reject Dialog -->
    <v-dialog v-model="rejectDialog" max-width="500">
      <v-card>
        <v-card-title>Rechazar Presupuesto</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectReason"
            label="Motivo del Rechazo"
            rows="3"
            required
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="rejectDialog = false">Cancelar</v-btn>
          <v-btn color="error" @click="rejectBudget" :loading="actionLoading">Rechazar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';

const route = useRoute();
const budget = ref(null);
const actionLoading = ref(false);

const approveDialog = ref(false);
const approveData = ref({ approved_amount: 0, approval_notes: '' });
const rejectDialog = ref(false);
const rejectReason = ref('');

const user = JSON.parse(localStorage.getItem('user') || '{}');
const isAdmin = computed(() => user.role === 'admin');

const canPerformActions = computed(() => {
  if (!budget.value) return false;
  if (budget.value.status === 'draft') return true;
  if (budget.value.status === 'pending' && isAdmin.value) return true;
  if (budget.value.status === 'approved') return true;
  return false;
});

const formatNumber = (num) => {
  return Number(num || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('es-VE');
};

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    pending: 'warning',
    approved: 'success',
    rejected: 'error',
    executed: 'info',
  };
  return colors[status] || 'grey';
};

const loadBudget = async () => {
  try {
    budget.value = await api.get(`budgets/${route.params.id}/`);
    approveData.value.approved_amount = parseFloat(budget.value.requested_amount);
  } catch (e) {
    console.error(e);
  }
};

const submitBudget = async () => {
  actionLoading.value = true;
  try {
    await api.post(`budgets/${budget.value.id}/submit/`);
    loadBudget();
  } catch (e) {
    alert('Error: ' + (e.data?.error || e.message));
  } finally {
    actionLoading.value = false;
  }
};

const openApproveDialog = () => {
  approveData.value = {
    approved_amount: parseFloat(budget.value.requested_amount),
    approval_notes: ''
  };
  approveDialog.value = true;
};

const approveBudget = async () => {
  actionLoading.value = true;
  try {
    await api.post(`budgets/${budget.value.id}/approve/`, approveData.value);
    approveDialog.value = false;
    loadBudget();
  } catch (e) {
    alert('Error: ' + (e.data?.error || e.message));
  } finally {
    actionLoading.value = false;
  }
};

const openRejectDialog = () => {
  rejectReason.value = '';
  rejectDialog.value = true;
};

const rejectBudget = async () => {
  actionLoading.value = true;
  try {
    await api.post(`budgets/${budget.value.id}/reject/`, {
      rejection_reason: rejectReason.value
    });
    rejectDialog.value = false;
    loadBudget();
  } catch (e) {
    alert('Error: ' + (e.data?.error || e.message));
  } finally {
    actionLoading.value = false;
  }
};

const executeBudget = async () => {
  if (!confirm('¿Está seguro? Esto agregará los repuestos al inventario.')) return;
  
  actionLoading.value = true;
  try {
    await api.post(`budgets/${budget.value.id}/execute/`);
    loadBudget();
  } catch (e) {
    alert('Error: ' + (e.data?.error || e.message));
  } finally {
    actionLoading.value = false;
  }
};

onMounted(() => {
  loadBudget();
});
</script>
