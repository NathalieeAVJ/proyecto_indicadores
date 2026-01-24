<template>
  <v-container>
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Números Telefónicos</h1>
        <v-btn color="primary" @click="openDialog()">
          <v-icon start>mdi-plus</v-icon>
          Nuevo Número
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-data-table :headers="headers" :items="phones" :loading="loadingTable" class="elevation-1">
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
          {{ isEdit ? 'Editar Número' : 'Nuevo Número' }}
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveItem" ref="formRef">
            <v-text-field
              v-model="form.number"
              label="Número Telefónico"
              required
              :rules="[v => !!v || 'Requerido']"
            ></v-text-field>
            <v-text-field
              v-model="form.description"
              label="Descripción / Alias"
            ></v-text-field>
            <v-text-field
              v-model="form.department"
              label="Departamento"
            ></v-text-field>
            <v-text-field
              v-model="form.location"
              label="Ubicación"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="saveItem" :loading="saving">
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

const phones = ref([]);
const loadingTable = ref(false);
const dialog = ref(false);
const saving = ref(false);
const isEdit = ref(false);
const formRef = ref(null);
const editedId = ref(null);

const form = ref({
  number: '',
  description: '',
  department: '',
  location: '',
});

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Número', key: 'number' },
  { title: 'Descripción', key: 'description' },
  { title: 'Departamento', key: 'department' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const loadPhones = async () => {
  loadingTable.value = true;
  try {
    phones.value = await api.get('phones/');
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
      number: '',
      description: '',
      department: '',
      location: '',
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
      await api.patch(`phones/${editedId.value}/`, form.value);
    } else {
      await api.post('phones/', form.value);
    }
    dialog.value = false;
    loadPhones();
  } catch (e) {
    console.error(e);
    alert('Error al guardar: ' + (e.data?.detail || e.message));
  } finally {
    saving.value = false;
  }
};

const deleteItem = async (item) => {
  if (confirm('¿Seguro que desea eliminar este número?')) {
    try {
      await api.delete(`phones/${item.id}/`);
      loadPhones();
    } catch (e) {
      console.error(e);
      alert('Error al eliminar');
    }
  }
};

onMounted(loadPhones);
</script>
