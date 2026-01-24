<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <h1 class="text-h4">Inventario de Repuestos</h1>
      </v-col>
      <v-col cols="12" md="6" class="text-right">
        <v-btn color="primary" @click="openFormDialog()">
          <v-icon start>mdi-plus</v-icon>
          Nuevo Repuesto
        </v-btn>
      </v-col>
    </v-row>

    <!-- Stats Cards -->
    <v-row class="mb-4">
      <v-col cols="12" md="4">
        <v-card color="primary" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-icon size="48" class="mr-4">mdi-package-variant-closed</v-icon>
            <div>
              <div class="text-h4">{{ stats.total_items || 0 }}</div>
              <div class="text-body-2">Total Repuestos</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card color="warning" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-icon size="48" class="mr-4">mdi-alert</v-icon>
            <div>
              <div class="text-h4">{{ stats.low_stock_count || 0 }}</div>
              <div class="text-body-2">Stock Bajo</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card color="success" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-icon size="48" class="mr-4">mdi-currency-usd</v-icon>
            <div>
              <div class="text-h4">${{ formatNumber(stats.total_inventory_value || 0) }}</div>
              <div class="text-body-2">Valor Total</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Buscar por nombre o código"
              prepend-inner-icon="mdi-magnify"
              clearable
              @update:model-value="debounceSearch"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedCategory"
              :items="categories"
              item-title="name"
              item-value="id"
              label="Categoría"
              clearable
              @update:model-value="loadParts"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-switch
              v-model="showLowStock"
              label="Solo stock bajo"
              color="warning"
              @update:model-value="loadParts"
            ></v-switch>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Parts Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="parts"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:item.quantity_in_stock="{ item }">
          <v-chip
            :color="item.is_low_stock ? 'warning' : 'success'"
            small
          >
            {{ item.quantity_in_stock }}
          </v-chip>
        </template>

        <template v-slot:item.unit_price="{ item }">
          ${{ formatNumber(item.unit_price) }}
        </template>

        <template v-slot:item.total_value="{ item }">
          ${{ formatNumber(item.total_value) }}
        </template>

        <template v-slot:item.category_detail="{ item }">
          {{ item.category_detail?.name || 'Sin categoría' }}
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" color="info" class="mr-1" @click="openAddStockDialog(item)" title="Agregar Stock">
            <v-icon>mdi-plus-box</v-icon>
          </v-btn>
          <v-btn icon size="small" color="primary" class="mr-1" @click="openFormDialog(item)" title="Editar">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn icon size="small" color="secondary" :to="`/spare-parts/${item.id}`" title="Ver Detalle / Historial">
            <v-icon>mdi-eye</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- FORM DIALOG (CREATE/EDIT) -->
    <v-dialog v-model="formDialog" max-width="700">
      <v-card>
        <v-card-title>
          {{ isEdit ? 'Editar Repuesto' : 'Nuevo Repuesto' }}
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="savePart" ref="formRef">
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.code"
                  label="Código"
                  required
                  :rules="[v => !!v || 'Código requerido']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="form.name"
                  label="Nombre del Repuesto"
                  required
                  :rules="[v => !!v || 'Nombre requerido']"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.category"
                  :items="categories"
                  item-title="name"
                  item-value="id"
                  label="Categoría"
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.location"
                  label="Ubicación en Almacén"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-textarea
              v-model="form.description"
              label="Descripción"
              rows="2"
            ></v-textarea>
            
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="form.unit_price"
                  label="Precio Unitario (USD)"
                  type="number"
                  min="0"
                  step="0.01"
                  prefix="$"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="form.quantity_in_stock"
                  label="Stock Actual"
                  type="number"
                  min="0"
                  :disabled="isEdit"
                  hint="Para editar stock use el botón '+' en la lista"
                  persistent-hint
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="form.minimum_stock"
                  label="Stock Mínimo"
                  type="number"
                  min="0"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="formDialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="savePart" :loading="saving">
            {{ isEdit ? 'Actualizar' : 'Guardar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add Stock Dialog -->
    <v-dialog v-model="addStockDialog" max-width="400">
      <v-card>
        <v-card-title>Agregar Stock</v-card-title>
        <v-card-text>
          <p class="mb-4 font-weight-bold">{{ selectedPart?.name }}</p>
          <v-text-field
            v-model.number="stockToAdd"
            label="Cantidad a agregar"
            type="number"
            min="1"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="addStockDialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="addStock" :loading="addingStock">Agregar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';

const parts = ref([]);
const categories = ref([]);
const stats = ref({});
const loading = ref(false);
const search = ref('');
const selectedCategory = ref(null);
const showLowStock = ref(false);

const addStockDialog = ref(false);
const stockToAdd = ref(1);
const addingStock = ref(false);

const formDialog = ref(false);
const formRef = ref(null);
const saving = ref(false);
const isEdit = ref(false);
const selectedPart = ref(null);

const form = ref({
  code: '',
  name: '',
  category: null,
  description: '',
  unit_price: 0,
  quantity_in_stock: 0,
  minimum_stock: 5,
  location: '',
});

const headers = [
  { title: 'Código', key: 'code' },
  { title: 'Nombre', key: 'name' },
  { title: 'Categoría', key: 'category_detail' },
  { title: 'Stock', key: 'quantity_in_stock', align: 'center' },
  { title: 'Mínimo', key: 'minimum_stock', align: 'center' },
  { title: 'Precio Unit.', key: 'unit_price', align: 'end' },
  { title: 'Valor Total', key: 'total_value', align: 'end' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const formatNumber = (num) => {
  return Number(num || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

let searchTimeout;
const debounceSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadParts(), 300);
};

const loadParts = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (search.value) params.append('search', search.value);
    if (selectedCategory.value) params.append('category', selectedCategory.value);
    if (showLowStock.value) params.append('low_stock', 'true');
    
    parts.value = await api.get(`spare-parts/?${params.toString()}`);
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const loadCategories = async () => {
  try {
    categories.value = await api.get('spare-part-categories/');
  } catch (e) {
    console.error(e);
  }
};

const loadStats = async () => {
  try {
    stats.value = await api.get('spare-parts/statistics/');
  } catch (e) {
    console.error(e);
  }
};

const openFormDialog = (part = null) => {
  if (part) {
    isEdit.value = true;
    selectedPart.value = part;
    form.value = { 
      ...part,
      category: part.category
    };
  } else {
    isEdit.value = false;
    selectedPart.value = null;
    form.value = {
      code: '',
      name: '',
      category: null,
      description: '',
      unit_price: 0,
      quantity_in_stock: 0,
      minimum_stock: 5,
      location: '',
    };
  }
  formDialog.value = true;
};

const savePart = async () => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;
  
  saving.value = true;
  try {
    if (isEdit.value) {
      await api.patch(`spare-parts/${selectedPart.value.id}/`, form.value);
    } else {
      await api.post('spare-parts/', form.value);
    }
    formDialog.value = false;
    loadParts();
    loadStats();
  } catch (e) {
    console.error(e);
    alert('Error al guardar: ' + (e.data?.detail || e.message));
  } finally {
    saving.value = false;
  }
};

const openAddStockDialog = (part) => {
  selectedPart.value = part;
  stockToAdd.value = 1;
  addStockDialog.value = true;
};

const addStock = async () => {
  addingStock.value = true;
  try {
    await api.post(`spare-parts/${selectedPart.value.id}/add_stock/`, {
      quantity: stockToAdd.value
    });
    addStockDialog.value = false;
    loadParts();
    loadStats();
  } catch (e) {
    alert('Error al agregar stock');
    console.error(e);
  } finally {
    addingStock.value = false;
  }
};

onMounted(() => {
  loadParts();
  loadCategories();
  loadStats();
});
</script>
