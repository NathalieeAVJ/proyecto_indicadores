<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <h1 class="text-h4 font-weight-bold">Estructura Organizacional</h1>
        <p class="text-subtitle-1 text-grey">Jerarquía y Funciones Departamentales de NatTelf</p>
      </v-col>
      <v-col cols="12" md="6" class="text-right">
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog()">Nuevo Departamento</v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="rounded-lg">
          <v-data-table
            :headers="headers"
            :items="departments"
            :loading="loading"
            class="elevation-0"
          >
            <template v-slot:item.parent_name="{ item }">
              <v-chip v-if="item.parent_name" color="info" size="small" variant="tonal">
                {{ item.parent_name }}
              </v-chip>
              <v-chip v-else color="primary" size="small" variant="flat">Nivel Raíz</v-chip>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small" variant="text" color="primary" @click="openDialog(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" variant="text" color="error" @click="deleteItem(item)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- CRUD DIALOG -->
    <v-dialog v-model="dialog" max-width="600" persistent>
      <v-card class="rounded-xl pa-2">
        <v-card-title class="text-h5 d-flex justify-space-between align-center">
          <span>{{ isEdit ? 'Editar Departamento' : 'Nuevo Departamento' }}</span>
          <v-btn icon variant="text" @click="dialog = false"><v-icon>mdi-close</v-icon></v-btn>
        </v-card-title>
        <v-divider class="mb-4"></v-divider>
        <v-card-text>
          <v-form @submit.prevent="saveItem" id="deptForm">
            <v-text-field
              v-model="form.name"
              label="Nombre del Departamento"
              required
              variant="outlined"
            ></v-text-field>

            <v-select
              v-model="form.parent"
              :items="departments"
              item-title="name"
              item-value="id"
              label="Departamento Superior (Jerarquía)"
              clearable
              variant="outlined"
              hint="Opcional: Define a qué departamento pertenece"
              persistent-hint
              class="mb-4"
            ></v-select>

            <v-textarea
              v-model="form.description"
              label="Funciones Específicas / Misión"
              rows="4"
              variant="outlined"
              counter
              placeholder="Describa las responsabilidades principales de esta área..."
            ></v-textarea>
            
            <button type="submit" style="display:none"></button>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" type="submit" form="deptForm" :loading="saving" size="large">
            {{ isEdit ? 'Actualizar' : 'Crear Área' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const departments = ref([]);
const loading = ref(true);
const dialog = ref(false);
const saving = ref(false);
const isEdit = ref(false);
const editedId = ref(null);

const headers = [
  { title: 'Departamento', key: 'name' },
  { title: 'Pertenece a', key: 'parent_name' },
  { title: 'Funciones', key: 'description' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const form = ref({
  name: '',
  parent: null,
  description: ''
});

const loadDepartments = async () => {
  loading.value = true;
  try {
    departments.value = await api.get('departments/');
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
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
    form.value = { name: '', parent: null, description: '' };
  }
  dialog.value = true;
};

const saveItem = async () => {
  if (!form.value.name) return;
  
  saving.value = true;
  try {
    if (isEdit.value) {
      await api.patch(`departments/${editedId.value}/`, form.value);
    } else {
      await api.post('departments/', form.value);
    }
    dialog.value = false;
    loadDepartments();
  } catch (e) {
    console.error(e);
    alert('Error al guardar departamento');
  } finally {
    saving.value = false;
  }
};

const deleteItem = async (item) => {
  if (confirm(`¿Eliminar departamento ${item.name}?`)) {
    try {
      await api.delete(`departments/${item.id}/`);
      loadDepartments();
    } catch (e) {
      alert('No se puede eliminar (posiblemente tiene sub-departamentos o empleados vinculados)');
    }
  }
};

onMounted(loadDepartments);
</script>
