<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Editar Usuario</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
               <v-autocomplete
                 v-model="form.employee_id"
                 :items="availableEmployees"
                 item-title="full_name"
                 item-value="id"
                 label="Vincular a Empleado (Obligatorio)"
                 required
                 @update:model-value="onEmployeeSelect"
               ></v-autocomplete>

              <v-text-field v-model="form.username" label="Usuario" required></v-text-field>
              <v-text-field v-model="form.email" label="Email" type="email" readonly></v-text-field>
               <v-text-field v-model="form.first_name" label="Nombre" readonly></v-text-field>
              <v-text-field v-model="form.last_name" label="Apellido" readonly></v-text-field>
              
              <v-select
                v-model="form.role"
                :items="roles"
                item-title="title"
                item-value="value"
                label="Rol"
                required
              ></v-select>

              <v-alert type="info" dense class="mb-3">Dejar contraseña en blanco para mantener la actual.</v-alert>
              <v-text-field v-model="form.password" label="Nueva Contraseña" type="password"></v-text-field>

              <v-btn color="primary" type="submit" :loading="loading" class="mt-4">Actualizar</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useRouter, useRoute } from 'vue-router';

const form = ref({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: '',
    employee_id: null
});

const availableEmployees = ref([]);

const loadEmployees = async (currentLinkedId = null) => {
    try {
        const emps = await api.get('employees/');
        // Available = No user linked OR it IS the current linked one
        availableEmployees.value = emps
            .filter(e => !e.system_user_name || e.id === currentLinkedId) 
            .map(e => ({ ...e, full_name: `${e.first_name} ${e.last_name} (${e.dni})` }));
    } catch (e) { console.error(e); }
};

const onEmployeeSelect = (empId) => {
    const emp = availableEmployees.value.find(e => e.id === empId);
    if (emp) {
        form.value.first_name = emp.first_name;
        form.value.last_name = emp.last_name;
        form.value.email = emp.email;
    }
};

const roles = [
    { title: 'Administrador', value: 'admin' },
    { title: 'Evaluador', value: 'evaluator' },
    { title: 'Soporte', value: 'support' },
    { title: 'Técnico', value: 'technician' },
];

const loading = ref(false);
const router = useRouter();
const route = useRoute();

const submit = async () => {
    loading.value = true;
    try {
        const data = { ...form.value };
        if (!data.password) delete data.password;
        
        await api.patch(`users/${route.params.id}/`, data);
        router.push('/users');
    } catch (e) {
        console.error(e);
        alert('Error al actualizar');
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
    try {
        const res = await api.get(`users/${route.params.id}/`);
        
        // Find which employee is currently linked to this user
        const emps = await api.get('employees/');
        const linkedEmp = emps.find(e => e.system_user === res.id);
        
        form.value = { ...res, password: '', employee_id: linkedEmp ? linkedEmp.id : null };
        
        // Load list respecting current link
        await loadEmployees(linkedEmp ? linkedEmp.id : null);
    } catch (e) {
        console.error(e);
    }
});
</script>
