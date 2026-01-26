<template>
  <v-container>
    <v-row>
      <v-col class="d-flex justify-space-between align-center">
        <h1 class="text-h4">Control de Nómina</h1>
        <v-btn color="secondary" @click="showGenerationDialog = true" prepend-icon="mdi-calculator">Generar Mes</v-btn>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12" md="2">
        <v-select v-model="filterMonth" :items="months" label="Mes" hide-details density="compact" @update:model-value="fetchPayroll"></v-select>
      </v-col>
      <v-col cols="12" md="2">
        <v-text-field v-model="filterYear" label="Año" type="number" hide-details density="compact" @change="fetchPayroll"></v-text-field>
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center">
        <v-text-field v-model="search" prepend-inner-icon="mdi-magnify" label="Buscar por nombre o Cédula..." hide-details density="compact" variant="solo-filled" class="mr-2"></v-text-field>
      </v-col>
      <v-col cols="12" md="3" class="d-flex align-center">
        <v-btn color="error" block prepend-icon="mdi-file-pdf-box" @click="exportPayrollReport" variant="tonal">Reporte Nómina</v-btn>
      </v-col>
      <v-col cols="12" md="3" class="d-flex align-center">
        <v-btn color="success" block prepend-icon="mdi-cash-check" @click="emitPaymentOrder" :disabled="payrolls.length === 0 || allPaid">Dar Orden de Pago</v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-data-table
            :headers="headers"
            :items="payrolls"
            :loading="loading"
            :search="search"
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
const search = ref('');
const loading = ref(true);
const now = new Date();
const filterMonth = ref(now.getMonth() + 1);
const filterYear = ref(now.getFullYear());
const showGenerationDialog = ref(false);
const generating = ref(false);
const genMonth = ref(now.getMonth() + 1);
const genYear = ref(now.getFullYear());

const months = [
  { title: 'Enero', value: 1 }, { title: 'Febrero', value: 2 }, { title: 'Marzo', value: 3 },
  { title: 'Abril', value: 4 }, { title: 'Mayo', value: 5 }, { title: 'Junio', value: 6 },
  { title: 'Julio', value: 7 }, { title: 'Agosto', value: 8 }, { title: 'Septiembre', value: 9 },
  { title: 'Octubre', value: 10 }, { title: 'Noviembre', value: 11 }, { title: 'Diciembre', value: 12 }
];

const headers = [
  { title: 'Cédula', key: 'employee_detail.dni' },
  { title: 'Nombre', key: 'employee_detail.first_name' },
  { title: 'Cargo', key: 'employee_detail.position' },
  { title: 'Sueldo Base', key: 'base_salary' },
  { title: 'Bonos', key: 'bonuses' },
  { title: 'Neto', key: 'net_salary' },
  { title: 'Estado', key: 'payment_status' },
];

const allPaid = computed(() => {
    return payrolls.value.length > 0 && payrolls.value.every(p => p.payment_status === 'paid');
});

const emitPaymentOrder = async () => {
    if (!confirm('¿Está seguro de emitir la ORDEN DE PAGO para todo el personal en este periodo?')) return;
    
    loading.value = true;
    try {
        await api.post('payroll/bulk_pay/', {
            month: filterMonth.value,
            year: filterYear.value
        });
        await fetchPayroll();
        alert('Orden de Pago emitida exitosamente. La nómina ha sido marcada como PAGADA.');
    } catch (e) {
        console.error(e);
        alert('Error al emitir la orden de pago');
    } finally {
        loading.value = false;
    }
};

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
    const headers = ['Cédula', 'Empleado', 'Cargo', 'Sueldo', 'Bonos', 'Neto', 'Estado'];
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
