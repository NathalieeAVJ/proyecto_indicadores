<template>
  <v-container fluid>
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="6">
        <h1 class="text-h4 font-weight-bold">Ventas de SIM & eSIM</h1>
        <p class="text-subtitle-1 text-grey">Punto de Venta (POS) y Gestión de Activaciones</p>
      </v-col>
      <v-col cols="12" md="6" class="text-right">
        <v-btn color="success" size="large" prepend-icon="mdi-plus" @click="openSellDialog">
          Nueva Venta / Activación
        </v-btn>
      </v-col>
    </v-row>

    <!-- Stats Dashboard -->
    <v-row class="mb-6">
      <v-col cols="12" md="3" v-for="(stat, index) in dashboardStats" :key="index">
        <v-card variant="outlined" class="rounded-xl border-dashed">
          <v-card-text>
            <div class="d-flex align-center">
              <v-avatar :color="stat.color + '-lighten-4'" size="48" class="mr-4">
                <v-icon :color="stat.color" size="24">{{ stat.icon }}</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption text-grey">{{ stat.label }}</div>
                <div class="text-h5 font-weight-bold">{{ stat.value }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card variant="outlined" class="rounded-xl">
      <v-tabs v-model="tab" color="primary" bg-color="grey-lighten-4">
        <v-tab value="catalog" prepend-icon="mdi-list-box-outline">Catálogo de Números</v-tab>
        <v-tab value="sales" prepend-icon="mdi-history">Historial de Ventas</v-tab>
        <v-tab value="customers" prepend-icon="mdi-account-group">Clientes</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <!-- TAB: Catalog -->
        <v-window-item value="catalog">
          <v-data-table
            :headers="catalogHeaders"
            :items="simCards"
            :loading="loading"
            class="elevation-0"
          >
            <template v-slot:item.type="{ item }">
              <v-chip :color="item.type === 'esim' ? 'info' : 'secondary'" size="x-small" variant="flat">
                {{ item.type_display }}
              </v-chip>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="getStatusColor(item.status)" size="x-small">
                {{ item.status_display }}
              </v-chip>
            </template>
            <template v-slot:item.phone_number_detail="{ item }">
              <span v-if="item.phone_number_detail" class="font-weight-bold text-primary">
                {{ item.phone_number_detail.number }}
              </span>
              <span v-else class="text-grey italic">No asignado</span>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn
                v-if="item.status === 'available'"
                color="success"
                variant="text"
                size="small"
                prepend-icon="mdi-cart"
                @click="startSaleWithSim(item)"
              >
                Vender
              </v-btn>
              <v-btn
                v-if="item.status === 'sold' && item.type === 'physical'"
                color="info"
                variant="text"
                size="small"
                prepend-icon="mdi-swap-horizontal"
                @click="openMigrateDialog(item)"
              >
                Migrar eSIM
              </v-btn>
            </template>
          </v-data-table>
        </v-window-item>

        <!-- TAB: Sales -->

        <v-window-item value="sales">
          <v-data-table
            :headers="saleHeaders"
            :items="sales"
            :loading="loading"
            class="elevation-0"
          >
            <template v-slot:item.amount="{ item }">
              <span class="font-weight-bold">${{ Number(item.amount).toLocaleString() }}</span>
            </template>
            <template v-slot:item.sale_date="{ item }">
              {{ formatDate(item.sale_date) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn icon="mdi-file-pdf-box" size="small" color="error" variant="text"></v-btn>
            </template>
          </v-data-table>
        </v-window-item>

        <!-- TAB: Customers -->
        <v-window-item value="customers">
          <v-data-table
            :headers="customerHeaders"
            :items="customers"
            :loading="loading"
            class="elevation-0"
          >
          </v-data-table>
        </v-window-item>
      </v-window>
    </v-card>

    <!-- SALE DIALOG (WIZARD) -->
    <v-dialog v-model="sellDialog" max-width="800" persistent>
      <v-card class="rounded-xl overflow-hidden">
        <v-toolbar color="primary" title="Proceso de Venta / Activación"></v-toolbar>
        
        <v-stepper v-model="step" :items="['SIM / eSIM', 'Cliente', 'Pago']" class="elevation-0">
          <template v-slot:item.1>
            <v-card-text class="pa-6">
              <h3 class="text-h6 mb-4">Seleccione SIM e Inventario</h3>
              <v-row>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="saleData.sim_card"
                    :items="availableSims"
                    item-title="iccid"
                    item-value="id"
                    label="Seleccionar SIM por ICCID"
                    variant="outlined"
                    hint="Solo se muestran SIMs disponibles"
                    persistent-hint
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props" :subtitle="item.raw.type_display + ' - ' + (item.raw.phone_number_detail?.number || 'Sin número')"></v-list-item>
                    </template>
                  </v-select>
                </v-col>
                <v-col cols="12" md="6" v-if="selectedSim">
                  <v-alert
                    density="compact"
                    :color="selectedSim.type === 'esim' ? 'info' : 'primary'"
                    variant="tonal"
                    :icon="selectedSim.type === 'esim' ? 'mdi-qrcode' : 'mdi-sim'"
                  >
                    <strong>Número:</strong> {{ selectedSim.phone_number_detail?.number || 'PENDIENTE ASIGNACIÓN' }}<br>
                    <strong>PIN:</strong> {{ selectedSim.pin }} | <strong>PUK:</strong> {{ selectedSim.puk }}
                  </v-alert>
                </v-col>
              </v-row>
            </v-card-text>
          </template>

          <template v-slot:item.2>
            <v-card-text class="pa-6">
              <div class="d-flex justify-space-between align-center mb-4">
                <h3 class="text-h6">Datos del Cliente</h3>
                <v-btn-toggle v-model="customerType" mandatory density="compact" color="primary">
                  <v-btn value="existing">Existente</v-btn>
                  <v-btn value="new">Nuevo</v-btn>
                </v-btn-toggle>
              </div>

              <v-row v-if="customerType === 'existing'">
                <v-col cols="12">
                  <v-autocomplete
                    v-model="saleData.customer"
                    :items="customers"
                    item-title="name"
                    item-value="id"
                    label="Buscar Cliente por Nombre o Cédula"
                    variant="outlined"
                    prepend-inner-icon="mdi-account-search"
                  ></v-autocomplete>
                </v-col>
              </v-row>

              <v-row v-else>
                <v-col cols="12" md="6">
                  <v-text-field v-model="newCustomer.name" label="Nombre Completo" variant="outlined"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="newCustomer.dni" label="Cédula / RIF" variant="outlined"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="newCustomer.email" label="Email" variant="outlined"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="newCustomer.phone" label="Teléfono" variant="outlined"></v-text-field>
                </v-col>
              </v-row>
            </v-card-text>
          </template>

          <template v-slot:item.3>
            <v-card-text class="pa-6 text-center">
              <v-icon size="64" color="success">mdi-cash-register</v-icon>
              <h3 class="text-h6 mt-4">Confirmar Transacción</h3>
              <div class="text-h3 font-weight-black my-4 text-primary">${{ saleData.amount }}</div>
              
              <v-row justify="center">
                <v-col cols="12" md="8">
                  <v-select
                    v-model="saleData.payment_method"
                    :items="paymentMethods"
                    label="Método de Pago"
                    variant="outlined"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="8">
                  <v-textarea v-model="saleData.notes" label="Notas / Observaciones" variant="outlined" rows="2"></v-textarea>
                </v-col>
              </v-row>

              <v-alert v-if="saleSuccess" type="success" variant="tonal" class="mt-4">
                ¡Venta completada con éxito!<br>
                <v-btn color="success" class="mt-2" v-if="selectedSim?.type === 'esim'">Descargar QR de Activación</v-btn>
              </v-alert>
            </v-card-text>
          </template>
        </v-stepper>

        <v-divider></v-divider>
        <v-card-actions class="pa-4 bg-grey-lighten-4">
          <v-btn variant="text" @click="sellDialog = false">Cancelar</v-btn>
          <v-spacer></v-spacer>
          <v-btn v-if="step > 1" variant="tonal" @click="step--" :disabled="saving">Anterior</v-btn>
          <v-btn 
            v-if="step < 3" 
            color="primary" 
            @click="step++" 
            :disabled="!canContinue"
          >
            Siguiente
          </v-btn>
          <v-btn 
            v-else 
            color="success" 
            variant="elevated" 
            @click="processSale" 
            :loading="saving"
            :disabled="saleSuccess"
          >
            Finalizar Venta
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- MIGRATION DIALOG -->
    <v-dialog v-model="migrateDialog" max-width="600">
      <v-card class="rounded-xl">
        <v-card-title class="bg-info text-white">Migración Física a eSIM</v-card-title>
        <v-card-text class="pa-6">
          <v-alert type="warning" variant="tonal" class="mb-4" density="compact">
            Esta acción desactivará permanentemente la SIM física actual y asignará el número a una nueva eSIM.
          </v-alert>
          
          <div v-if="simToMigrate" class="mb-6">
            <div class="text-caption text-grey">SIM Actual</div>
            <div class="text-h6 font-weight-bold">{{ simToMigrate.phone_number_detail?.number }}</div>
            <div class="text-caption">ICCID: {{ simToMigrate.iccid }}</div>
          </div>

          <v-select
            v-model="newEsimId"
            :items="availableEsims"
            item-title="iccid"
            item-value="id"
            label="Seleccionar Nueva eSIM (Stock)"
            variant="outlined"
            prepend-inner-icon="mdi-qrcode"
          >
            <template v-slot:item="{ props, item }">
              <v-list-item v-bind="props" subtitle="eSIM Disponible"></v-list-item>
            </template>
          </v-select>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-btn variant="text" @click="migrateDialog = false">Cancelar</v-btn>
          <v-spacer></v-spacer>
          <v-btn 
            color="info" 
            variant="elevated" 
            @click="processMigration" 
            :loading="saving"
            :disabled="!newEsimId"
          >
            Confirmar Migración
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '@/services/api';
import { formatDate } from '@/utils/format';

const tab = ref('catalog');
const loading = ref(false);
const saving = ref(false);
const step = ref(1);
const sellDialog = ref(false);
const saleSuccess = ref(false);
const migrateDialog = ref(false);
const simToMigrate = ref(null);
const newEsimId = ref(null);

const simCards = ref([]);
const sales = ref([]);
const customers = ref([]);
const dashboard = ref({});

const customerType = ref('existing');
const saleData = ref({
  sim_card: null,
  customer: null,
  amount: 25.00,
  payment_method: 'cash',
  notes: ''
});

const newCustomer = ref({
  name: '',
  dni: '',
  email: '',
  phone: '',
  address: 'Calle San Juan, Caracas'
});

const paymentMethods = [
  { title: 'Efectivo', value: 'cash' },
  { title: 'Tarjeta / Débito', value: 'card' },
  { title: 'Transferencia', value: 'transfer' },
  { title: 'Zelle', value: 'zelle' },
];

const catalogHeaders = [
  { title: 'ICCID', key: 'iccid' },
  { title: 'Tipo', key: 'type' },
  { title: 'Número', key: 'phone_number_detail' },
  { title: 'Estado', key: 'status' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' },
];

const saleHeaders = [
  { title: 'ID', key: 'id' },
  { title: 'Cliente', key: 'customer_name' },
  { title: 'SIM (ICCID)', key: 'sim_card_iccid' },
  { title: 'Monto', key: 'amount' },
  { title: 'Método', key: 'payment_method_display' },
  { title: 'Fecha', key: 'sale_date' },
  { title: 'Vendedor', key: 'seller_name' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' },
];

const customerHeaders = [
  { title: 'Cédula', key: 'dni' },
  { title: 'Nombre', key: 'name' },
  { title: 'Email', key: 'email' },
  { title: 'Teléfono', key: 'phone' },
];

const dashboardStats = computed(() => [
  { label: 'Ventas Totales', value: dashboard.value.total_sales_count || 0, icon: 'mdi-cart-check', color: 'success' },
  { label: 'Ingresos Mensuales', value: `$${Number(dashboard.value.month_sales_amount || 0).toLocaleString()}`, icon: 'mdi-currency-usd', color: 'primary' },
  { label: 'SIMs Físicas', value: dashboard.value.sims_available || 0, icon: 'mdi-sim', color: 'orange' },
  { label: 'eSIMs Disponibles', value: dashboard.value.esims_available || 0, icon: 'mdi-qrcode', color: 'info' },
]);

const availableSims = computed(() => simCards.value.filter(s => s.status === 'available'));
const availableEsims = computed(() => simCards.value.filter(s => s.status === 'available' && s.type === 'esim'));

const selectedSim = computed(() => {
  if (!saleData.value.sim_card) return null;
  return simCards.value.find(s => s.id === saleData.value.sim_card);
});

const canContinue = computed(() => {
  if (step.value === 1) return !!saleData.value.sim_card;
  if (step.value === 2) {
    if (customerType.value === 'existing') return !!saleData.value.customer;
    return !!newCustomer.value.name && !!newCustomer.value.dni;
  }
  return true;
});

const openMigrateDialog = (sim) => {
  simToMigrate.value = sim;
  newEsimId.value = null;
  migrateDialog.value = true;
};

const processMigration = async () => {
  saving.value = true;
  try {
    await api.post(`ventas/sim-cards/${simToMigrate.value.id}/migrate_to_esim/`, {
      new_esim_id: newEsimId.value
    });
    alert('Migración física a eSIM completada con éxito.');
    migrateDialog.value = false;
    loadData();
  } catch (e) {
    alert(e.message || 'Error al procesar la migración');
  } finally {
    saving.value = false;
  }
};

const loadData = async () => {
  loading.value = true;
  try {
    const [simsRes, salesRes, customersRes, dashRes] = await Promise.all([
      api.get('ventas/sim-cards/'),
      api.get('ventas/sales/'),
      api.get('ventas/customers/'),
      api.get('ventas/sales/dashboard/')
    ]);
    simCards.value = simsRes;
    sales.value = salesRes;
    customers.value = customersRes;
    dashboard.value = dashRes;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const openSellDialog = () => {
  step.value = 1;
  saleSuccess.value = false;
  saleData.value = { sim_card: null, customer: null, amount: 25.00, payment_method: 'cash', notes: '' };
  sellDialog.value = true;
};

const startSaleWithSim = (sim) => {
  openSellDialog();
  saleData.value.sim_card = sim.id;
};

const processSale = async () => {
  saving.value = true;
  try {
    let customerId = saleData.value.customer;
    
    // Si el cliente es nuevo, crearlo primero
    if (customerType.value === 'new') {
      const createdCustomer = await api.post('ventas/customers/', newCustomer.value);
      customerId = createdCustomer.id;
    }
    
    // Realizar la venta
    await api.post('ventas/sales/', {
      ...saleData.value,
      customer: customerId
    });
    
    saleSuccess.value = true;
    setTimeout(() => {
      sellDialog.value = false;
      loadData();
    }, 2000);
    
  } catch (e) {
    alert(e.message || 'Error al procesar la venta');
  } finally {
    saving.value = false;
  }
};

const getStatusColor = (status) => {
  const colors = { available: 'success', sold: 'grey', defective: 'error' };
  return colors[status] || 'grey';
};

onMounted(loadData);
</script>

<style scoped>
.border-dashed {
  border-style: dashed !important;
}
</style>
