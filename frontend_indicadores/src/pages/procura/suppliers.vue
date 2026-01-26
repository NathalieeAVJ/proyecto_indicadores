<template>
  <v-container fluid>
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="6">
        <h1 class="text-h4 font-weight-bold">Portal de Proveedores</h1>
        <p class="text-subtitle-1 text-grey">Gestión de proveedores, contratos y evaluaciones</p>
      </v-col>
      <v-col cols="12" md="6" class="text-right">
        <v-btn color="primary" prepend-icon="mdi-office-building-plus" @click="openSupplierDialog">
          Registrar Proveedor
        </v-btn>
      </v-col>
    </v-row>
    
    <!-- Tabs -->
    <v-card variant="outlined" class="rounded-xl">
      <v-tabs v-model="tab" color="primary" bg-color="grey-lighten-4">
        <v-tab value="suppliers" prepend-icon="mdi-office-building">Proveedores</v-tab>
        <v-tab value="contracts" prepend-icon="mdi-file-document-edit">Contratos</v-tab>
        <v-tab value="orders" prepend-icon="mdi-cart">Órdenes de Compra</v-tab>
        <v-tab value="evaluations" prepend-icon="mdi-star">Evaluaciones</v-tab>
      </v-tabs>
      
      <v-window v-model="tab">
        <!-- TAB: Proveedores -->
        <v-window-item value="suppliers">
          <v-card-text>
            <v-row class="mb-4">
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="searchSuppliers"
                  prepend-inner-icon="mdi-magnify"
                  label="Buscar proveedor..."
                  variant="outlined"
                  density="compact"
                  hide-details
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="filterCategory"
                  :items="categoryOptions"
                  label="Filtrar por categoría"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                ></v-select>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col v-for="supplier in filteredSuppliers" :key="supplier.id" cols="12" md="4">
                <v-card variant="outlined" class="rounded-xl hover-card" @click="viewSupplierDashboard(supplier)">
                  <v-card-text>
                    <div class="d-flex justify-space-between align-start mb-3">
                      <div>
                        <h3 class="text-h6 font-weight-bold">{{ supplier.name }}</h3>
                        <p class="text-caption text-grey">{{ supplier.rif }}</p>
                      </div>
                      <v-chip
                        :color="getStatusColor(supplier.status)"
                        size="small"
                        variant="flat"
                      >
                        {{ supplier.status_display }}
                      </v-chip>
                    </div>
                    
                    <v-divider class="my-3"></v-divider>
                    
                    <div class="d-flex align-center mb-2">
                      <v-icon size="small" class="mr-2">mdi-star</v-icon>
                      <v-rating
                        :model-value="supplier.rating"
                        readonly
                        density="compact"
                        size="small"
                        color="warning"
                      ></v-rating>
                      <span class="text-caption ml-2">({{ supplier.evaluation_count }})</span>
                    </div>
                    
                    <div class="text-caption">
                      <v-icon size="small">mdi-tag</v-icon>
                      {{ supplier.category_display }}
                    </div>
                    <div class="text-caption">
                      <v-icon size="small">mdi-file-document</v-icon>
                      {{ supplier.active_contracts_count }} contratos activos
                    </div>
                  </v-card-text>
                  <v-card-actions class="pa-4 pt-0">
                    <v-btn size="small" variant="text" color="info" prepend-icon="mdi-eye" @click.stop="viewSupplierDashboard(supplier)">
                      Ver Dashboard
                    </v-btn>
                    <v-spacer></v-spacer>
                    <v-btn icon="mdi-pencil" size="small" variant="text" @click.stop="editSupplier(supplier)"></v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-window-item>
        
        <!-- TAB: Contratos -->
        <v-window-item value="contracts">
          <v-card-text>
            <v-btn color="primary" prepend-icon="mdi-plus" class="mb-4" @click="openContractDialog">
              Nuevo Contrato
            </v-btn>
            
            <v-data-table
              :headers="contractHeaders"
              :items="contracts"
              :loading="loading"
              class="elevation-0"
            >
              <template v-slot:item.is_active="{ item }">
                <v-chip :color="item.is_active ? 'success' : 'grey'" size="small">
                  {{ item.is_active ? 'Vigente' : 'Inactivo' }}
                </v-chip>
              </template>
              <template v-slot:item.value="{ item }">
                <span class="font-weight-bold">${{ Number(item.value).toLocaleString() }}</span>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>
        
        <!-- TAB: Órdenes de Compra -->
        <v-window-item value="orders">
          <v-card-text>
            <v-btn color="secondary" prepend-icon="mdi-cart-plus" class="mb-4" @click="openOrderDialog">
              Nueva Orden de Compra
            </v-btn>
            
            <v-data-table
              :headers="orderHeaders"
              :items="purchaseOrders"
              :loading="loading"
              class="elevation-0"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="getOrderStatusColor(item.status)" size="x-small">
                  {{ item.status_display }}
                </v-chip>
              </template>
              <template v-slot:item.total_amount="{ item }">
                ${{ Number(item.total_amount).toLocaleString() }}
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn
                  v-if="item.status === 'pending'"
                  icon="mdi-check"
                  size="x-small"
                  variant="text"
                  color="success"
                  @click="approveOrder(item.id)"
                ></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>
        
        <!-- TAB: Evaluaciones -->
        <v-window-item value="evaluations">
          <v-card-text>
            <v-btn color="warning" prepend-icon="mdi-star" class="mb-4" @click="openEvaluationDialog">
              Nueva Evaluación
            </v-btn>
            
            <v-data-table
              :headers="evaluationHeaders"
              :items="evaluations"
              :loading="loading"
              class="elevation-0"
            >
              <template v-slot:item.overall_score="{ item }">
                <v-rating
                  :model-value="item.overall_score"
                  readonly
                  density="compact"
                  size="small"
                  color="warning"
                ></v-rating>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>
      </v-window>
    </v-card>
    
    <!-- DIALOGS (simplificados por espacio) -->
    <v-dialog v-model="supplierDialog" max-width="700">
      <v-card class="rounded-xl">
        <v-card-title class="bg-primary text-white">
          {{ isEditSupplier ? 'Editar Proveedor' : 'Registrar Nuevo Proveedor' }}
        </v-card-title>
        <v-card-text class="pa-6">
          <v-form ref="supplierFormRef">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field v-model="formSupplier.name" label="Nombre o Razón Social" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="formSupplier.rif" label="RIF/NIT" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formSupplier.email" label="Email" variant="outlined" type="email"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formSupplier.phone" label="Teléfono" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="formSupplier.address" label="Dirección" variant="outlined" rows="2"></v-textarea>
              </v-col>
              <v-col cols="12" md="6">
                <v-select v-model="formSupplier.category" :items="categoryOptions" label="Categoría" variant="outlined"></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select v-model="formSupplier.status" :items="statusOptions" label="Estado" variant="outlined"></v-select>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4 bg-grey-lighten-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="supplierDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="elevated" @click="saveSupplier" :loading="saving">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Dashboard Dialog -->
    <v-dialog v-model="dashboardDialog" max-width="900">
      <v-card v-if="selectedSupplier" class="rounded-xl">
        <v-card-title class="bg-info text-white">
          Dashboard: {{ selectedSupplier.name }}
        </v-card-title>
        <v-card-text class="pa-6">
          <v-row>
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h4 font-weight-bold text-primary">{{ dashboardData.total_contracts }}</div>
                  <div class="text-caption">Contratos Totales</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h4 font-weight-bold text-success">{{ dashboardData.active_contracts }}</div>
                  <div class="text-caption">Contratos Activos</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h4 font-weight-bold text-warning">{{ dashboardData.purchase_orders }}</div>
                  <div class="text-caption">Órdenes de Compra</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h4 font-weight-bold text-purple">{{ dashboardData.avg_rating }}</div>
                  <div class="text-caption">Calificación</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dashboardDialog = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';

const tab = ref('suppliers');
const loading = ref(false);
const saving = ref(false);

const suppliers = ref([]);
const contracts = ref([]);
const purchaseOrders = ref([]);
const evaluations = ref([]);

const searchSuppliers = ref('');
const filterCategory = ref(null);

const supplierDialog = ref(false);
const dashboardDialog = ref(false);
const isEditSupplier = ref(false);
const selectedSupplier = ref(null);

const dashboardData = ref({
  total_contracts: 0,
  active_contracts: 0,
  purchase_orders: 0,
  avg_rating: 0
});

const formSupplier = ref({
  name: '',
  rif: '',
  email: '',
  phone: '',
  address: '',
  category: 'other',
  status: 'active'
});

const categoryOptions = [
  { title: 'Materiales y Equipos', value: 'materials' },
  { title: 'Servicios Técnicos', value: 'services' },
  { title: 'Construcción', value: 'construction' },
  { title: 'Mantenimiento', value: 'maintenance' },
  { title: 'Consultoría', value: 'consulting' },
  { title: 'Transporte y Logística', value: 'transport' },
  { title: 'Otros', value: 'other' },
];

const statusOptions = [
  { title: 'Activo', value: 'active' },
  { title: 'Inactivo', value: 'inactive' },
  { title: 'Bloqueado', value: 'blocked' },
];

const contractHeaders = [
  { title: 'Nº Contrato', key: 'contract_number' },
  { title: 'Proveedor', key: 'supplier_name' },
  { title: 'Título', key: 'title' },
  { title: 'Valor', key: 'value' },
  { title: 'Estado', key: 'is_active', align: 'center' },
];

const orderHeaders = [
  { title: 'Nº Orden', key: 'order_number' },
  { title: 'Proveedor', key: 'supplier_name' },
  { title: 'Monto', key: 'total_amount' },
  { title: 'Estado', key: 'status', align: 'center' },
  { title: 'Acciones', key: 'actions', align: 'end', sortable: false },
];

const evaluationHeaders = [
  { title: 'Proveedor', key: 'supplier_name' },
  { title: 'Evaluador', key: 'evaluator_name' },
  { title: 'Fecha', key: 'evaluation_date' },
  { title: 'Calificación', key: 'overall_score' },
];

const filteredSuppliers = computed(() => {
  let result = suppliers.value;
  
  if (searchSuppliers.value) {
    const q = searchSuppliers.value.toLowerCase();
    result = result.filter(s => 
      s.name.toLowerCase().includes(q) || 
      s.rif.toLowerCase().includes(q) ||
      s.email.toLowerCase().includes(q)
    );
  }
  
  if (filterCategory.value) {
    result = result.filter(s => s.category === filterCategory.value);
  }
  
  return result;
});

const loadData = async () => {
  loading.value = true;
  try {
    const [suppliersRes, contractsRes, ordersRes, evaluationsRes] = await Promise.all([
      api.get('procura/suppliers/'),
      api.get('procura/contracts/'),
      api.get('procura/purchase-orders/'),
      api.get('procura/evaluations/')
    ]);
    
    suppliers.value = suppliersRes;
    contracts.value = contractsRes;
    purchaseOrders.value = ordersRes;
    evaluations.value = evaluationsRes;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const openSupplierDialog = () => {
  isEditSupplier.value = false;
  formSupplier.value = { name: '', rif: '', email: '', phone: '', address: '', category: 'other', status: 'active' };
  supplierDialog.value = true;
};

const editSupplier = (supplier) => {
  isEditSupplier.value = true;
  formSupplier.value = { ...supplier };
  supplierDialog.value = true;
};

const saveSupplier = async () => {
  saving.value = true;
  try {
    if (isEditSupplier.value) {
      await api.patch(`procura/suppliers/${formSupplier.value.id}/`, formSupplier.value);
    } else {
      await api.post('procura/suppliers/', formSupplier.value);
    }
    supplierDialog.value = false;
    loadData();
  } catch (e) {
    alert('Error al guardar proveedor');
  } finally {
    saving.value = false;
  }
};

const viewSupplierDashboard = async (supplier) => {
  selectedSupplier.value = supplier;
  try {
    const data = await api.get(`procura/suppliers/${supplier.id}/dashboard/`);
    dashboardData.value = data;
    dashboardDialog.value = true;
  } catch (e) {
    alert('Error al cargar dashboard');
  }
};

const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    inactive: 'grey',
    blocked: 'error'
  };
  return colors[status] || 'grey';
};

const getOrderStatusColor = (status) => {
  const colors = {
    pending: 'warning',
    approved: 'info',
    received: 'success',
    cancelled: 'error'
  };
  return colors[status] || 'grey';
};

const approveOrder = async (orderId) => {
  try {
    await api.patch(`procura/purchase-orders/${orderId}/approve/`);
    loadData();
  } catch (e) {
    alert('Error al aprobar orden');
  }
};

const openContractDialog = () => {
  alert('Función de nuevo contrato - implementar dialog similar');
};

const openOrderDialog = () => {
  alert('Función de nueva orden - implementar dialog similar');
};

const openEvaluationDialog = () => {
  alert('Función de nueva evaluación - implementar dialog similar');
};

onMounted(loadData);
</script>

<style scoped>
.hover-card:hover {
  border-color: var(--v-primary-base) !important;
  background-color: #f8faff;
  transition: all 0.3s ease;
}
</style>
