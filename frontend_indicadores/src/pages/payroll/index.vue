<template>
  <v-container>
    <v-row>
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Control de Nómina</h1>
        <v-btn color="secondary" @click="showGenerationDialog = true" prepend-icon="mdi-calculator">Generar Mes</v-btn>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12" md="3">
        <v-select v-model="filterMonth" :items="months" label="Mes" @update:model-value="fetchPayroll"></v-select>
      </v-col>
      <v-col cols="12" md="3">
        <v-text-field v-model="filterYear" label="Año" type="number" @change="fetchPayroll"></v-text-field>
      </v-col>
      <v-col cols="12" md="6" class="d-flex align-center pt-5">
        <v-btn color="error" prepend-icon="mdi-file-pdf-box" @click="exportPayrollReport" variant="tonal">Reporte General de Nómina</v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-data-table
            :headers="headers"
            :items="payrolls"
            :loading="loading"
          >
            <template v-slot:item.net_salary="{ item }">
              <span class="font-weight-bold">${{ parseFloat(item.net_salary).toLocaleString() }}</span>
            </template>
            <template v-slot:item.payment_status="{ item }">
              <v-chip :color="item.payment_status === 'paid' ? 'success' : 'warning'" size="small">
                {{ item.payment_status === 'paid' ? 'PAGADO' : 'PENDIENTE' }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Generation Dialog -->
    <v-dialog v-model="showGenerationDialog" max-width="500px">
        <v-card title="Generar Nómina Mensual">
            <v-card-text>
                <p class="mb-4">Esto creará registros de nómina para todos los empleados activos que aún no tengan registro para el periodo seleccionado.</p>
                <v-select v-model="genMonth" :items="months" label="Mes a Generar"></v-select>
                <v-text-field v-model="genYear" label="Año" type="number"></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn @click="showGenerationDialog = false">Cancelar</v-btn>
                <v-btn color="primary" @click="generatePayroll" :loading="generating">Procesar Nómina</v-btn>
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
import { formatDate } from '@/utils/format';

const authStore = useAuthStore();

const payrolls = ref([]);
const loading = ref(true);
const filterMonth = ref(12);
const filterYear = ref(2026);
const showGenerationDialog = ref(false);
const generating = ref(false);
const genMonth = ref(1);
const genYear = ref(2026);

const months = [
  { title: 'Enero', value: 1 }, { title: 'Febrero', value: 2 }, { title: 'Marzo', value: 3 },
  { title: 'Abril', value: 4 }, { title: 'Mayo', value: 5 }, { title: 'Junio', value: 6 },
  { title: 'Julio', value: 7 }, { title: 'Agosto', value: 8 }, { title: 'Septiembre', value: 9 },
  { title: 'Octubre', value: 10 }, { title: 'Noviembre', value: 11 }, { title: 'Diciembre', value: 12 }
];

const headers = [
  { title: 'Empleado', key: 'employee_detail.dni' },
  { title: 'Nombre', key: 'employee_detail.first_name' },
  { title: 'Cargo', key: 'employee_detail.position' },
  { title: 'Sueldo Base', key: 'base_salary' },
  { title: 'Bonos', key: 'bonuses' },
  { title: 'Neto', key: 'net_salary' },
  { title: 'Estado', key: 'payment_status' },
];

const fetchPayroll = async () => {
  loading.value = true;
  try {
    const response = await api.get(`payroll/?month=${filterMonth.value}&year=${filterYear.value}`);
    payrolls.value = response;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const generatePayroll = async () => {
    generating.value = true;
    try {
        await api.post('payroll/generate_month/', {
            month: genMonth.value,
            year: genYear.value
        });
        showGenerationDialog.value = false;
        fetchPayroll();
        alert('Nómina generada con éxito');
    } catch (e) {
        console.error(e);
        alert('Error al generar la nómina');
    } finally {
        generating.value = false;
    }
};

const exportPayrollReport = async () => {
    const headers = ['DNI', 'Empleado', 'Cargo', 'Sueldo', 'Bonos', 'Neto', 'Estado'];
    const body = payrolls.value.map(p => [
        p.employee_detail?.dni || 'N/A',
        `${p.employee_detail?.first_name} ${p.employee_detail?.last_name}`,
        p.employee_detail?.position || 'N/A',
        `$${p.base_salary}`,
        `$${p.bonuses}`,
        `$${p.net_salary}`,
        p.payment_status.toUpperCase()
    ]);

    const monthName = months.find(m => m.value === filterMonth.value)?.title;

    await generatePDFReport({
        title: 'Reporte General de Nómina',
        subtitle: `Periodo: ${monthName} ${filterYear.value}`,
        headers: headers,
        body: body,
        filename: `Nomina_NatTelf_${monthName}_${filterYear.value}.pdf`,
        author: authStore.user?.username || 'Sistema NatTelf',
        metadata: {
            'Departamento': 'Finanzas / RRHH',
            'Total Empleados': body.length,
            'Moneda': 'USD'
        }
    });
};

onMounted(fetchPayroll);
</script>
