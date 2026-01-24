<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title class="text-h5 pa-4">
            {{ isEdit ? 'Editar Empleado' : 'Nuevo Empleado' }}
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pa-6">
            <v-form @submit.prevent="save">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.first_name" label="Nombre" required></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.last_name" label="Apellido" required></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.dni" label="Cédula/ID" required></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.status"
                    :items="statuses"
                    item-title="title"
                    item-value="value"
                    label="Estado Laboral"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.email" label="Correo" type="email"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.phone" label="Teléfono"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.position" label="Cargo"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.department" label="Departamento"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.hire_date" label="Fecha Ingreso" type="date"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field v-model="form.base_salary" label="Sueldo Base" type="number" prefix="$"></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.rank"
                    :items="hierarchyLevels"
                    item-title="title"
                    item-value="value"
                    label="Nivel Jerárquico"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="6">
                  <v-autocomplete
                    v-model="form.supervisor"
                    :items="supervisors"
                    item-title="full_name"
                    item-value="id"
                    label="Supervisor Directo"
                    clearable
                  ></v-autocomplete>
                </v-col>
                <v-col cols="12">
                  <v-textarea v-model="form.address" label="Dirección" rows="2"></v-textarea>
                </v-col>
              </v-row>

              <div class="d-flex justify-end mt-4">
                <v-btn color="grey-lighten-1" variant="text" class="me-2" @click="router.back()">Cancelar</v-btn>
                <v-btn color="primary" type="submit" :loading="loading">
                  {{ isEdit ? 'Actualizar' : 'Guardar' }}
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/services/api';

const router = useRouter();
const route = useRoute();
const isEdit = computed(() => !!route.params.id);
const loading = ref(false);

const form = ref({
  first_name: '',
  last_name: '',
  dni: '',
  email: '',
  phone: '',
  address: '',
  position: '',
  department: '',
  hire_date: new Date().toISOString().substr(0, 10),
  base_salary: 0,
  status: 'active',
  rank: 5,
  supervisor: null
});

const supervisors = ref([]);

const hierarchyLevels = [
  { title: 'Presidente (Nivel 0)', value: 0 },
  { title: 'Vice Presidente (Nivel 1)', value: 1 },
  { title: 'Gerente General (Nivel 2)', value: 2 },
  { title: 'Gerente (Nivel 3)', value: 3 },
  { title: 'Coordinador (Nivel 4)', value: 4 },
  { title: 'Especialista / Operativo (Nivel 5)', value: 5 },
];

const statuses = [
  { title: 'Activo', value: 'active' },
  { title: 'En Vacaciones', value: 'vacation' },
  { title: 'Permiso/Reposo', value: 'on_leave' },
  { title: 'Retirado', value: 'retired' },
];

const save = async () => {
  loading.value = true;
  try {
    if (isEdit.value) {
      await api.patch(`employees/${route.params.id}/`, form.value);
    } else {
      await api.post('employees/', form.value);
    }
    router.push('/employees');
  } catch (e) {
    console.error(e);
    alert('Error al guardar datos del empleado');
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
    // Load potential supervisors (everyone with rank < 5 or everyone for now)
    try {
        const emps = await api.get('employees/');
        supervisors.value = emps.map(e => ({ ...e, full_name: `${e.first_name} ${e.last_name}` }));
    } catch (e) {
        console.error('Error loading supervisors', e);
    }

    if (isEdit.value) {
        try {
            const res = await api.get(`employees/${route.params.id}/`);
            form.value = res;
        } catch (e) {
            console.error(e);
        }
    }
});
</script>
