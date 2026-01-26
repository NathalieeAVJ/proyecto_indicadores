<template>
  <v-container>
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Radiobases</h1>
        <v-btn color="primary" @click="openDialog()">
          <v-icon start>mdi-plus</v-icon>
          Nueva Radiobase
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Buscar por nombre, código o ubicación..."
          single-line
          hide-details
          variant="solo-filled"
          density="compact"
          class="pa-2"
        ></v-text-field>
      </v-card-title>
      <v-data-table :headers="headers" :items="items" :loading="loadingTable" :search="search" class="elevation-1">
        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" variant="text" color="primary" class="me-2" @click="openDialog(item)">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn icon size="small" variant="text" color="error" @click="deleteItem(item)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- CRUD DIALOG -->
    <v-dialog v-model="dialog" max-width="700">
      <v-card>
        <v-card-title>
          {{ isEdit ? 'Editar Radiobase' : 'Nueva Radiobase' }}
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveItem" ref="formRef" id="rbForm">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="form.name"
                  label="Nombre de la Radiobase"
                  required
                  :rules="[v => !!v || 'Requerido']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.code"
                  label="Código de Estación"
                  required
                  :rules="[v => !!v || 'Requerido']"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-text-field
              v-model="form.location"
              label="Ubicación / Dirección"
            ></v-text-field>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="form.latitude"
                  label="Latitud"
                  type="number"
                  step="0.000001"
                  prepend-inner-icon="mdi-map-marker"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="form.longitude"
                  label="Longitud"
                  type="number"
                  step="0.000001"
                  prepend-inner-icon="mdi-map-marker-outline"
                ></v-text-field>
              </v-col>
            </v-row>
            <button type="submit" style="display:none"></button>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" type="submit" form="rbForm" :loading="saving">
            {{ isEdit ? 'Actualizar' : 'Guardar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const items = ref([]);
const search = ref('');
const loadingTable = ref(false);
const dialog = ref(false);
const saving = ref(false);
const isEdit = ref(false);
const formRef = ref(null);
const editedId = ref(null);

const form = ref({
  name: '',
  code: '',
  location: '',
  latitude: null,
  longitude: null,
});

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Nombre', key: 'name' },
  { title: 'Código', key: 'code' },
  { title: 'Ubicación', key: 'location' },
  { title: 'Lat/Long', key: 'latitude', value: item => item.latitude ? `${item.latitude}, ${item.longitude}` : '-' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const loadItems = async () => {
  loadingTable.value = true;
  try {
    items.value = await api.get('radio-bases/');
  } catch (e) {
    console.error(e);
  } finally {
    loadingTable.value = false;
  }
};

const openDialog = (item = null) => {
  if (item) {
    isEdit.value = true;
    editedId.value = item.id;
    form.value = { ...item };
  } else {
    isEdit.value = false;
    editedId.value = null;
    form.value = {
      name: '',
      code: '',
      location: '',
      latitude: null,
      longitude: null,
    };
  }
  dialog.value = true;
};

const saveItem = async () => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;

  saving.value = true;
  try {
    if (isEdit.value) {
      await api.patch(`radio-bases/${editedId.value}/`, form.value);
    } else {
      await api.post('radio-bases/', form.value);
    }
    dialog.value = false;
    loadItems();
  } catch (e) {
    console.error(e);
    alert('Error al guardar: ' + (e.data?.detail || e.message));
  } finally {
    saving.value = false;
  }
};

const deleteItem = async (item) => {
  if (confirm('¿Seguro que desea eliminar esta radiobase?')) {
    try {
      await api.delete(`radio-bases/${item.id}/`);
      loadItems();
    } catch (e) {
      console.error(e);
      alert('Error al eliminar');
    }
  }
};

onMounted(loadItems);
</script>
