<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn variant="text" to="/spare-parts" class="mb-4">
          <v-icon start>mdi-arrow-left</v-icon>
          Volver al Inventario
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-if="part">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>{{ part.name }}</span>
            <v-chip :color="part.is_low_stock ? 'warning' : 'success'">
              Stock: {{ part.quantity_in_stock }}
            </v-chip>
          </v-card-title>
          <v-card-subtitle>{{ part.code }}</v-card-subtitle>
          <v-card-text>
            <v-row>
              <v-col cols="6" md="3">
                <div class="text-body-2 text-medium-emphasis">Categoría</div>
                <div>{{ part.category_detail?.name || 'Sin categoría' }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-body-2 text-medium-emphasis">Precio Unitario</div>
                <div>${{ formatNumber(part.unit_price) }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-body-2 text-medium-emphasis">Stock Mínimo</div>
                <div>{{ part.minimum_stock }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-body-2 text-medium-emphasis">Ubicación</div>
                <div>{{ part.location || '-' }}</div>
              </v-col>
            </v-row>
            <v-divider class="my-4"></v-divider>
            <div class="text-body-2 text-medium-emphasis">Descripción</div>
            <div>{{ part.description || 'Sin descripción' }}</div>
          </v-card-text>
          <v-card-actions>
            <v-btn color="info" @click="openAddStockDialog">
              <v-icon start>mdi-plus-box</v-icon>
              Agregar Stock
            </v-btn>
            <v-btn color="primary" @click="editMode = true">
              <v-icon start>mdi-pencil</v-icon>
              Editar
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Usage History -->
        <v-card class="mt-4">
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Historial de Uso</span>
            <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" label="Buscar uso..." hide-details density="compact" variant="solo-filled" style="max-width: 250px;"></v-text-field>
          </v-card-title>
          <v-data-table
            :headers="usageHeaders"
            :items="usages"
            :loading="loadingUsages"
            :search="search"
            class="elevation-0"
          >
            <template v-slot:item.used_at="{ item }">
              {{ formatDate(item.used_at) }}
            </template>
            <template v-slot:item.total_cost="{ item }">
              ${{ formatNumber(item.total_cost) }}
            </template>
            <template v-slot:item.incident="{ item }">
              {{ item.incident_type === 'phone' ? 'Teléfono' : 'Radiobase' }} #{{ item.incident_id }}
            </template>
          </v-data-table>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card color="primary" variant="tonal">
          <v-card-text>
            <div class="text-h3 text-center">${{ formatNumber(part.total_value) }}</div>
            <div class="text-center text-body-2">Valor Total en Inventario</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Add Stock Dialog -->
    <v-dialog v-model="addStockDialog" max-width="400">
      <v-card>
        <v-form @submit.prevent="addStock" id="addStockForm">
            <v-card-title>Agregar Stock</v-card-title>
            <v-card-text>
              <v-text-field
                v-model.number="stockToAdd"
                label="Cantidad a agregar"
                type="number"
                min="1"
              ></v-text-field>
              <button type="submit" style="display:none"></button>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn @click="addStockDialog = false">Cancelar</v-btn>
              <v-btn color="primary" type="submit" form="addStockForm" :loading="addingStock">Agregar</v-btn>
            </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';

const route = useRoute();
const part = ref(null);
const usages = ref([]);
const search = ref('');
const loadingUsages = ref(false);
const editMode = ref(false);

const addStockDialog = ref(false);
const stockToAdd = ref(1);
const addingStock = ref(false);

const usageHeaders = [
  { title: 'Fecha', key: 'used_at' },
  { title: 'Cantidad', key: 'quantity_used', align: 'center' },
  { title: 'Costo Total', key: 'total_cost', align: 'end' },
  { title: 'Incidencia', key: 'incident' },
  { title: 'Usuario', key: 'used_by_detail.username' },
];

const formatNumber = (num) => {
  return Number(num || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('es-VE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const loadPart = async () => {
  try {
    part.value = await api.get(`spare-parts/${route.params.id}/`);
  } catch (e) {
    console.error(e);
  }
};

const loadUsages = async () => {
  loadingUsages.value = true;
  try {
    usages.value = await api.get(`spare-part-usage/?spare_part=${route.params.id}`);
  } catch (e) {
    console.error(e);
  } finally {
    loadingUsages.value = false;
  }
};

const openAddStockDialog = () => {
  stockToAdd.value = 1;
  addStockDialog.value = true;
};

const addStock = async () => {
  addingStock.value = true;
  try {
    await api.post(`spare-parts/${route.params.id}/add_stock/`, {
      quantity: stockToAdd.value
    });
    addStockDialog.value = false;
    loadPart();
  } catch (e) {
    alert('Error al agregar stock');
    console.error(e);
  } finally {
    addingStock.value = false;
  }
};

onMounted(() => {
  loadPart();
  loadUsages();
});
</script>
