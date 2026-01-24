<template>
  <v-container>
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Gestión de Usuarios</h1>
        <v-btn color="primary" @click="openDialog()" prepend-icon="mdi-account-plus">
          Nuevo Usuario
        </v-btn>
      </v-col>
    </v-row>

    <v-card elevation="2">
      <v-data-table :headers="headers" :items="users" :loading="loadingTable" class="elevation-0">
        <template v-slot:item.date_joined="{ item }">
          {{ formatDate(item.date_joined) }}
        </template>
        <template v-slot:item.role="{ item }">
          <v-chip size="small" :color="roleColors[item.role] || 'grey'">
            {{ getRoleLabel(item.role) }}
          </v-chip>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" variant="text" color="primary" @click="openDialog(item)" title="Editar Usuario/Rol">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn icon size="small" variant="text" color="warning" @click="openPasswordDialog(item)" title="Cambiar Contraseña">
            <v-icon>mdi-key-variant</v-icon>
          </v-btn>
          <v-btn icon size="small" variant="text" color="error" @click="deleteItem(item)" title="Eliminar">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- CRUD DIALOG -->
    <v-dialog v-model="dialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="pa-4 text-h5">
          {{ isEdit ? 'Editar Usuario' : 'Nuevo Usuario' }}
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-form @submit.prevent="saveItem" ref="formRef">
            <v-autocomplete
              v-if="!isEdit"
              v-model="form.employee_id"
              :items="availableEmployees"
              item-title="full_name"
              item-value="id"
              label="Vincular a Empleado"
              required
              :rules="[v => !!v || 'Debe vincular un empleado']"
              @update:model-value="onEmployeeSelect"
            ></v-autocomplete>

            <v-text-field v-model="form.username" label="Usuario" required :rules="[v => !!v || 'Requerido']"></v-text-field>
            <v-text-field v-model="form.email" label="Email" type="email" :readonly="!isEdit" :disabled="!isEdit"></v-text-field>
            
            <v-row>
              <v-col cols="6"><v-text-field v-model="form.first_name" label="Nombre" readonly disabled></v-text-field></v-col>
              <v-col cols="6"><v-text-field v-model="form.last_name" label="Apellido" readonly disabled></v-text-field></v-col>
            </v-row>

            <v-text-field 
              v-if="!isEdit" 
              v-model="form.password" 
              label="Contraseña Inicial" 
              type="password" 
              required 
              :rules="[v => !!v || 'Contraseña requerida']"
            ></v-text-field>
            
            <v-select
              v-model="form.role"
              :items="roles"
              item-title="title"
              item-value="value"
              label="Rol del Sistema"
              required
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="saveItem" :loading="saving">
            {{ isEdit ? 'Actualizar' : 'Guardar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- PASSWORD RESET DIALOG -->
    <v-dialog v-model="passwordDialog" max-width="400">
      <v-card>
        <v-card-title>Cambiar Contraseña</v-card-title>
        <v-card-text>
          <p class="mb-4">Usuario: <strong>{{ selectedUser?.username }}</strong></p>
          <v-text-field
            v-model="newPassword"
            label="Nueva Contraseña"
            type="password"
            required
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="passwordDialog = false">Cancelar</v-btn>
          <v-btn color="warning" @click="resetPassword" :loading="saving">Cambiar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { formatDate } from '@/utils/format';

const users = ref([]);
const availableEmployees = ref([]);
const loadingTable = ref(true);
const dialog = ref(false);
const passwordDialog = ref(false);
const saving = ref(false);
const isEdit = ref(false);
const editedId = ref(null);
const selectedUser = ref(null);
const formRef = ref(null);
const newPassword = ref('');

const form = ref({
  username: '', email: '', first_name: '', last_name: '',
  password: '', role: 'support', employee_id: null
});

const roles = [
  { title: 'Administrador', value: 'admin' },
  { title: 'Evaluador', value: 'evaluator' },
  { title: 'Soporte', value: 'support' },
  { title: 'Técnico', value: 'technician' },
];

const roleColors = { admin: 'error', evaluator: 'secondary', support: 'info', technician: 'success' };

const headers = [
  { title: 'Usuario', key: 'username' },
  { title: 'Nombre Completo', key: 'full_name', value: item => `${item.first_name} ${item.last_name}` },
  { title: 'Email', key: 'email' },
  { title: 'Rol', key: 'role' },
  { title: 'Registro', key: 'date_joined' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const loadUsers = async () => {
  loadingTable.value = true;
  try {
    users.value = await api.get('users/');
  } catch (e) { console.error(e); }
  finally { loadingTable.value = false; }
};

const loadEmployees = async () => {
  try {
    const emps = await api.get('employees/');
    availableEmployees.value = emps
      .filter(e => !e.system_user_name)
      .map(e => ({ ...e, full_name: `${e.first_name} ${e.last_name} (${e.dni})` }));
  } catch (e) { console.error(e); }
};

const onEmployeeSelect = (empId) => {
  const emp = availableEmployees.value.find(e => e.id === empId);
  if (emp) {
    form.value.first_name = emp.first_name;
    form.value.last_name = emp.last_name;
    form.value.email = emp.email;
    if (!form.value.username) {
      form.value.username = (emp.first_name[0] + emp.last_name).toLowerCase().replace(/\s/g, '');
    }
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
    form.value = { username: '', email: '', first_name: '', last_name: '', password: '', role: 'support', employee_id: null };
    loadEmployees();
  }
  dialog.value = true;
};

const openPasswordDialog = (user) => {
  selectedUser.value = user;
  newPassword.value = '';
  passwordDialog.value = true;
};

const saveItem = async () => {
  const { valid } = await formRef.value.validate();
  if (!valid) return;

  saving.value = true;
  try {
    if (isEdit.value) {
      await api.patch(`users/${editedId.value}/`, { username: form.value.username, role: form.value.role });
    } else {
      await api.post('users/', form.value);
    }
    dialog.value = false;
    loadUsers();
  } catch (e) {
    console.error(e);
    alert('Error al guardar: ' + (e.data?.detail || 'Verifique los datos'));
  } finally { saving.value = false; }
};

const resetPassword = async () => {
  if (!newPassword.value) return;
  saving.value = true;
  try {
    await api.patch(`users/${selectedUser.value.id}/`, { password: newPassword.value });
    passwordDialog.value = false;
    alert('Contraseña actualizada');
  } catch (e) { alert('Error al cambiar contraseña'); }
  finally { saving.value = false; }
};

const deleteItem = async (item) => {
  if (confirm(`¿Eliminar usuario ${item.username}?`)) {
    await api.delete(`users/${item.id}/`);
    loadUsers();
  }
};

const getRoleLabel = (r) => roles.find(x => x.value === r)?.title || r;

onMounted(loadUsers);
</script>
