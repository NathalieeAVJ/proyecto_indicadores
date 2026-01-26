<template>
  <v-container>
    <v-row class="mb-4">
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Gestión de Personal</h1>
        <div>
          <v-btn color="primary" @click="openDialog()" prepend-icon="mdi-plus" class="mr-2">Nuevo Empleado</v-btn>
          <v-btn color="error" prepend-icon="mdi-file-pdf-box" @click="exportEmployeesReport" variant="tonal">Reporte PDF</v-btn>
        </div>
      </v-col>
    </v-row>

    <v-card elevation="2">
      <v-card-title>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Buscar empleado (Nombre, Cédula, Cargo...)"
          single-line
          hide-details
          variant="solo-filled"
          density="compact"
          class="pa-2"
        ></v-text-field>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="employees"
        :loading="loadingTable"
        :search="search"
        class="elevation-0"
      >
        <template v-slot:item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small">
            {{ item.status.toUpperCase() }}
          </v-chip>
        </template>
        <template v-slot:item.rank="{ item }">
           {{ getRankLabel(item.rank) }}
        </template>
        <template v-slot:item.department_ref="{ item }">
           {{ item.department_detail?.name || '-' }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" variant="text" color="primary" @click="openDialog(item)" title="Editar">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn icon size="small" variant="text" color="error" @click="openBlacklistDialog(item)" title="Desincorporar a Lista Negra">
            <v-icon>mdi-account-off</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- CRUD DIALOG -->
    <v-dialog v-model="dialog" max-width="900" persistent>
      <v-card>
        <v-card-title class="text-h5 pa-4">
          {{ isEdit ? 'Editar Empleado' : 'Nuevo Empleado' }}
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-form @submit.prevent="saveItem" ref="formRef" id="employeeForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.first_name" label="Nombre" required :rules="[v => !!v || 'Requerido']"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.last_name" label="Apellido" required :rules="[v => !!v || 'Requerido']"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="form.dni" label="Cédula" required :rules="[v => !!v || 'Requerido']"></v-text-field>
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
                <v-select
                  v-model="form.department_ref"
                  :items="departments"
                  item-title="name"
                  item-value="id"
                  label="Departamento Oficial"
                  clearable
                ></v-select>
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
            <!-- Hidden submit button for Enter support -->
            <button type="submit" style="display:none"></button>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" type="submit" form="employeeForm" :loading="saving">
            {{ isEdit ? 'Actualizar' : 'Guardar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- BLACKLIST REASON DIALOG -->
    <v-dialog v-model="blacklistDialog" max-width="500">
      <v-card class="rounded-xl">
        <v-card-title class="pa-4 bg-error text-white">
            Desincorporar Personal
        </v-card-title>
        <v-card-text class="pa-6">
            <p class="mb-4">¿Desea mover a <strong>{{ selectedForBlacklist?.first_name }} {{ selectedForBlacklist?.last_name }}</strong> a la lista negra?</p>
            <v-textarea
                v-model="blacklistReason"
                label="Motivo de Desincorporación / Cese"
                placeholder="Ej: Renuncia voluntaria, Despido justificado, etc."
                variant="outlined"
                rows="3"
                hide-details
            ></v-textarea>
            <p class="text-caption text-grey mt-3 italic">
                * El registro no se borrará, se mantendrá en el archivo histórico.<br>
                * Sus accesos al sistema serán revocados inmediatamente.
            </p>
        </v-card-text>
        <v-card-actions class="pa-4 px-6">
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="blacklistDialog = false">Cancelar</v-btn>
            <v-btn color="error" variant="elevated" @click="confirmBlacklist" :loading="savingBlacklist">Confirmar Salida</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { generatePDFReport } from '@/utils/reports';

const authStore = useAuthStore();
const employees = ref([]);
const supervisors = ref([]);
const search = ref('');
const loadingTable = ref(true);
const dialog = ref(false);
const isEdit = ref(false);
const editedId = ref(null);
const formRef = ref(null);

const blacklistDialog = ref(false);
const selectedForBlacklist = ref(null);
const blacklistReason = ref('');
const savingBlacklist = ref(false);

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
  supervisor: null,
  department_ref: null
});

const departments = ref([]);

const hierarchyLevels = [
  { title: 'Presidente (0)', value: 0 },
  { title: 'V.P. (1)', value: 1 },
  { title: 'Gte Gral (2)', value: 2 },
  { title: 'Gerente (3)', value: 3 },
  { title: 'Coordinador (4)', value: 4 },
  { title: 'Operativo (5)', value: 5 },
];

const statuses = [
  { title: 'Activo', value: 'active' },
  { title: 'Vacaciones', value: 'vacation' },
  { title: 'Permiso', value: 'on_leave' },
  { title: 'Retirado', value: 'retired' },
  { title: 'Lista Negra', value: 'blacklisted' },
];

const headers = [
  { title: 'Cédula', key: 'dni' },
  { title: 'Nombre', key: 'first_name' },
  { title: 'Apellido', key: 'last_name' },
  { title: 'Departamento', key: 'department_ref' },
  { title: 'Cargo', key: 'position' },
  { title: 'Nivel', key: 'rank' },
  { title: 'Supervisor', key: 'supervisor_name' },
  { title: 'Estado', key: 'status' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
];

const getStatusColor = (s) => {
  const map = { active: 'success', vacation: 'info', on_leave: 'warning', retired: 'orange', blacklisted: 'error' };
  return map[s] || 'grey';
};

const getRankLabel = (r) => {
  const levels = { 0: 'Pres.', 1: 'V.P.', 2: 'Gte Gral', 3: 'Gte', 4: 'Coord.', 5: 'Base' };
  return levels[r] || 'Base';
};

const fetchEmployees = async () => {
  loadingTable.value = true;
  try {
    const [empRes, deptRes] = await Promise.all([
      api.get('employees/'),
      api.get('departments/')
    ]);
    employees.value = empRes;
    supervisors.value = empRes.map(e => ({ ...e, full_name: `${e.first_name} ${e.last_name}` }));
    departments.value = deptRes;
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
      first_name: '', last_name: '', dni: '', email: '', phone: '', address: '',
      position: '', department: '', hire_date: new Date().toISOString().substr(0, 10),
      base_salary: 0, status: 'active', rank: 5, supervisor: null
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
      await api.patch(`employees/${editedId.value}/`, form.value);
    } else {
      await api.post('employees/', form.value);
    }
    dialog.value = false;
    fetchEmployees();
  } catch (e) {
    console.error(e);
    alert('Error al guardar');
  } finally {
    saving.value = false;
  }
};

const openBlacklistDialog = (item) => {
    selectedForBlacklist.value = item;
    blacklistReason.value = '';
    blacklistDialog.value = true;
};

const confirmBlacklist = async () => {
    if (!blacklistReason.value) {
        alert('Debe especificar un motivo');
        return;
    }
    savingBlacklist.value = true;
    try {
        await api.post(`employees/${selectedForBlacklist.value.id}/blacklist/`, {
            reason: blacklistReason.value
        });
        blacklistDialog.value = false;
        fetchEmployees();
    } catch (e) {
        alert('Error al desincorporar');
    } finally {
        savingBlacklist.value = false;
    }
};

const deleteItem = async (item) => {
  if (confirm(`¿ELIMINAR PERMANENTEMENTE a ${item.first_name}? Esta acción no se recomienda, use Lista Negra.`)) {
    await api.delete(`employees/${item.id}/`);
    fetchEmployees();
  }
};

const exportEmployeesReport = async () => {
    const reportHeaders = ['Cédula', 'Nombre', 'Apellido', 'Cargo', 'Departamento', 'Estado'];
    const body = employees.value.map(e => [
        e.dni, e.first_name, e.last_name, e.position, e.department, e.status.toUpperCase()
    ]);
    await generatePDFReport({
        title: 'Reporte de Capital Humano',
        subtitle: 'Censo General de Trabajadores',
        headers: reportHeaders,
        body: body,
        filename: `Reporte_Personal_${Date.now()}.pdf`,
        author: authStore.user?.username || 'Sistema',
    });
};

onMounted(fetchEmployees);
</script>
