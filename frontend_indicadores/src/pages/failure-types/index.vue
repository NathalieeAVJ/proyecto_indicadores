<template>
  <v-container>
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Tipos de Falla</h1>
        <v-btn color="primary" @click="openDialog()">
          <v-icon start>mdi-plus</v-icon>
          Nuevo Tipo
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Buscar tipo de falla..."
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
    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>
          {{ isEdit ? 'Editar Tipo de Falla' : 'Nuevo Tipo de Falla' }}
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveItem" ref="formRef" id="failureTypeForm">
            <v-text-field
              v-model="form.name"
              label="Nombre del Tipo de Falla"
              required
              :rules="[v => !!v || 'Requerido']"
            ></v-text-field>
            <v-textarea
              v-model="form.description"
              label="Descripción"
              rows="3"
            ></v-textarea>
            <button type="submit" style="display:none"></button>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" type="submit" form="failureTypeForm" :loading="saving">
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
  description: '',
});

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Nombre', key: 'name' },
  { title: 'Descripción', key: 'description' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const loadItems = async () => {
  loadingTable.value = true;
  try {
    items.value = await api.get('failure-types/');
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
      description: '',
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
      await api.patch(`failure-types/${editedId.value}/`, form.value);
    } else {
      await api.post('failure-types/', form.value);
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
  if (confirm('¿Seguro que desea eliminar este tipo de falla?')) {
    try {
      await api.delete(`failure-types/${item.id}/`);
      loadItems();
    } catch (e) {
      console.error(e);
      alert('Error al eliminar');
    }
  }
};

onMounted(loadItems);
</script>
