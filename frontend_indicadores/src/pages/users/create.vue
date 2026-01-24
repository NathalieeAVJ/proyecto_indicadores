<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Nuevo Usuario</v-card-title>
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

               <v-text-field v-model="form.username" label="Usuario" placeholder="ej: jvargas" required></v-text-field>
               <v-text-field v-model="form.email" label="Email" type="email" readonly></v-text-field>
               <v-text-field v-model="form.first_name" label="Nombre" readonly></v-text-field>
               <v-text-field v-model="form.last_name" label="Apellido" readonly></v-text-field>
              <v-text-field v-model="form.password" label="Contraseña" type="password" required></v-text-field>
              
              <v-select
                v-model="form.role"
                :items="roles"
                item-title="title"
                item-value="value"
                label="Rol"
                required
              ></v-select>

              <v-btn color="primary" type="submit" :loading="loading" class="mt-4">Guardar</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';

const form = ref({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'support',
    employee_id: null
});

const availableEmployees = ref([]);

const loadEmployees = async () => {
    try {
        const emps = await api.get('employees/');
        // Filter only those without a linked user_name (meaning no system_user linked in backend serializer data)
        // Note: The backend logic should ideally have a specific filter, but we filter here for now.
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
        // Suggest username based on name
        if (!form.value.username) {
            form.value.username = (emp.first_name[0] + emp.last_name).toLowerCase().replace(/\s/g, '');
        }
    }
};

import { onMounted } from 'vue';
onMounted(loadEmployees);

const roles = [
    { title: 'Administrador', value: 'admin' },
    { title: 'Evaluador', value: 'evaluator' },
    { title: 'Soporte', value: 'support' },
    { title: 'Técnico', value: 'technician' },
];

const loading = ref(false);
const router = useRouter();

const submit = async () => {
    loading.value = true;
    try {
        await api.post('users/', form.value);
        router.push('/users');
    } catch (e) {
        console.error(e);
        alert('Error al crear usuario');
    } finally {
        loading.value = false;
    }
};
</script>
