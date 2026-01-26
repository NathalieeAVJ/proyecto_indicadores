<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <h1 class="text-h4">Presupuestos</h1>
      </v-col>
      <v-col cols="12" md="6" class="text-right">
        <v-btn color="primary" @click="openCreateDialog">
          <v-icon start>mdi-plus</v-icon>
          Nuevo Presupuesto
        </v-btn>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              item-title="text"
              item-value="value"
              label="Estado"
              clearable
              hide-details
              @update:model-value="loadBudgets"
            ></v-select>
          </v-col>
          <v-col cols="12" md="8">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Buscar presupuesto por título o descripción..."
              single-line
              hide-details
              variant="solo-filled"
              density="compact"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Budgets Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="budgets"
        :loading="loading"
        :search="search"
        class="elevation-1"
      >
        <template v-slot:item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" small>
            {{ item.status_display }}
          </v-chip>
        </template>

        <template v-slot:item.requested_amount="{ item }">
          ${{ formatNumber(item.requested_amount) }}
        </template>

        <template v-slot:item.approved_amount="{ item }">
          <span v-if="item.approved_amount">
            ${{ formatNumber(item.approved_amount) }}
          </span>
          <span v-else class="text-medium-emphasis">-</span>
        </template>

        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" color="primary" :to="`/budgets/${item.id}`" title="Ver Detalle / Acciones">
            <v-icon>mdi-eye</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- CREATE BUDGET DIALOG -->
    <v-dialog v-model="createDialog" max-width="900" persistent>
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Nuevo Presupuesto</span>
          <v-btn icon variant="text" @click="createDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveBudget(false)" ref="formRef" id="budgetForm">
            <v-text-field
              v-model="form.title"
              label="Título del Presupuesto"
              required
              :rules="[v => !!v || 'Título requerido']"
            ></v-text-field>
            
            <v-textarea
              v-model="form.description"
              label="Descripción / Justificación"
              rows="2"
              required
              :rules="[v => !!v || 'Descripción requerida']"
            ></v-textarea>

            <v-divider class="my-4"></v-divider>
            <div class="d-flex justify-space-between align-center mb-3">
              <h3 class="text-subtitle-1 font-weight-bold">Repuestos a Solicitar</h3>
              <v-btn variant="tonal" size="small" color="primary" @click="addItem" type="button">
                <v-icon start>mdi-plus</v-icon>
                Agregar Item
              </v-btn>
            </div>

            <v-row v-for="(item, index) in form.items" :key="index" class="mb-2 align-center">
              <v-col cols="12" md="5">
                <v-autocomplete
                  v-model="item.spare_part"
                  :items="spareParts"
                  item-title="name"
                  item-value="id"
                  label="Repuesto"
                  density="compact"
                  required
                  @update:model-value="updateItemPrice(index)"
                >
                  <template v-slot:item="{ item: spareItem, props }">
                    <v-list-item v-bind="props">
                      <template v-slot:subtitle>
                        {{ spareItem.raw.code }} - Stock: {{ spareItem.raw.quantity_in_stock }}
                      </template>
                    </v-list-item>
                  </template>
                </v-autocomplete>
              </v-col>
              <v-col cols="4" md="2">
                <v-text-field
                  v-model.number="item.quantity"
                  label="Cant."
                  type="number"
                  min="1"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="4" md="2">
                <v-text-field
                  v-model.number="item.unit_price"
                  label="P. Unit."
                  type="number"
                  prefix="$"
                  step="0.01"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="3" md="2">
                <div class="text-right text-body-2 pt-2">
                  ${{ formatNumber(item.quantity * item.unit_price) }}
                </div>
              </v-col>
              <v-col cols="1" md="1" class="text-center">
                <v-btn icon color="error" variant="text" size="x-small" @click="removeItem(index)" v-if="form.items.length > 1" type="button">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>

            <v-row justify="end">
              <v-col cols="12" md="4">
                <v-card color="primary" variant="tonal" density="compact">
                  <v-card-text class="text-right py-2">
                    <div class="text-caption">Total Estimado</div>
                    <div class="text-h5 font-weight-bold">${{ formatNumber(totalAmount) }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <button type="submit" style="display:none"></button>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="createDialog = false">Cancelar</v-btn>
          <v-btn color="primary" type="submit" form="budgetForm" :loading="saving">
            Guardar Borrador
          </v-btn>
          <v-btn color="success" @click="saveBudget(true)" :loading="saving" type="button">
            Enviar para Aprobación
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';

const budgets = ref([]);
const spareParts = ref([]);
const loading = ref(false);
const search = ref('');
const statusFilter = ref(null);

const createDialog = ref(false);
const saving = ref(false);
const formRef = ref(null);

const form = ref({
  title: '',
  description: '',
  items: [{ spare_part: null, quantity: 1, unit_price: 0 }],
});

const statusOptions = [
  { text: 'Borrador', value: 'draft' },
  { text: 'Pendiente', value: 'pending' },
  { text: 'Aprobado', value: 'approved' },
  { text: 'Rechazado', value: 'rejected' },
  { text: 'Ejecutado', value: 'executed' },
];

const headers = [
  { title: '#', key: 'id', width: '60px' },
  { title: 'Título', key: 'title' },
  { title: 'Estado', key: 'status', align: 'center' },
  { title: 'Monto Solicitado', key: 'requested_amount', align: 'end' },
  { title: 'Monto Aprobado', key: 'approved_amount', align: 'end' },
  { title: 'Solicitado por', key: 'requested_by_detail.username' },
  { title: 'Fecha', key: 'created_at' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const totalAmount = computed(() => {
  return form.value.items.reduce((sum, item) => {
    return sum + (item.quantity * item.unit_price);
  }, 0);
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

const loadBudgets = async () => {
  loading.value = true;
  try {
    const params = statusFilter.value ? `?status=${statusFilter.value}` : '';
    budgets.value = await api.get(`budgets/${params}`);
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const loadSpareParts = async () => {
  try {
    spareParts.value = await api.get('spare-parts/');
  } catch (e) {
    console.error(e);
  }
};

const openCreateDialog = () => {
  form.value = {
    title: '',
    description: '',
    items: [{ spare_part: null, quantity: 1, unit_price: 0 }],
  };
  createDialog.value = true;
};

const addItem = () => {
  form.value.items.push({ spare_part: null, quantity: 1, unit_price: 0 });
};

const removeItem = (index) => {
  form.value.items.splice(index, 1);
};

const updateItemPrice = (index) => {
  const item = form.value.items[index];
  const part = spareParts.value.find(p => p.id === item.spare_part);
  if (part) {
    item.unit_price = parseFloat(part.unit_price);
  }
};

const saveBudget = async (sendForApproval = false) => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  
  if (form.value.items.length === 0 || !form.value.items[0].spare_part) {
    alert('Debe agregar al menos un repuesto');
    return;
  }
  
  saving.value = true;
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      requested_amount: totalAmount.value,
      items: form.value.items.filter(i => i.spare_part),
    };
    
    const budget = await api.post('budgets/', payload);
    
    if (sendForApproval) {
      await api.post(`budgets/${budget.id}/submit/`);
    }
    
    createDialog.value = false;
    loadBudgets();
  } catch (e) {
    console.error(e);
    alert('Error al crear presupuesto: ' + (e.message || 'Error desconocido'));
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  loadBudgets();
  loadSpareParts();
});
</script>
