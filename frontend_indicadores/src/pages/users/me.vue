<template>
  <v-container>
    <v-row>
      <!-- Part 1: Account Profile -->
      <v-col cols="12" md="4">
        <v-card class="elevation-2 rounded-lg mb-4">
          <v-toolbar color="primary" density="compact">
            <v-toolbar-title class="text-subtitle-1">Cuenta de Acceso</v-toolbar-title>
          </v-toolbar>
          <v-card-text class="text-center pa-6">
            <v-avatar size="100" color="secondary" class="mb-4">
              <v-icon size="60" color="white">mdi-account</v-icon>
            </v-avatar>
            <h2 class="text-h5 font-weight-bold">{{ authStore.user?.username }}</h2>
            <v-chip color="primary" size="small" class="mt-2" variant="flat">
              {{ getRoleLabel(authStore.user?.role) }}
            </v-chip>

            <v-divider class="my-6"></v-divider>

            <v-list class="text-left" density="compact">
              <v-list-item prepend-icon="mdi-email" :title="authStore.user?.email || 'N/A'" subtitle="Correo Electrónico"></v-list-item>
              <v-list-item prepend-icon="mdi-account-details" :title="`${authStore.user?.first_name} ${authStore.user?.last_name}`" subtitle="Nombre Completo"></v-list-item>
              <v-list-item prepend-icon="mdi-calendar" :title="formatDate(authStore.user?.date_joined)" subtitle="F. de Registro"></v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Part 2: Employee Portal (Self Service) -->
      <v-col cols="12" md="8">
        <div v-if="loading">
             <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
        <v-alert v-else-if="!employee" type="info" variant="tonal" icon="mdi-information">
            Este usuario no tiene un perfil de trabajador vinculado en RRHH. Las funciones de auto-gestión no están disponibles.
        </v-alert>
        
        <template v-else>
            <v-card title="Mis Servicios Laborales" class="rounded-lg mb-6 elevation-2">
                <v-card-text>
                    <p class="mb-6">Aquí tienes acceso a tus documentos oficiales vinculados a tu ficha laboral en NatTelf.</p>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-card border flat class="pa-4 bg-soft-purple h-100">
                                <v-icon color="primary" size="large" class="mb-2">mdi-file-certificate</v-icon>
                                <h3 class="text-h6 mb-2">Constancia de Trabajo</h3>
                                <p class="text-body-2 mb-4">Certificado oficial de tu cargo y relación laboral.</p>
                                <v-btn color="primary" block prepend-icon="mdi-download" @click="downloadWorkLetter" :loading="exporting">Generar Constancia</v-btn>
                            </v-card>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-card border flat class="pa-4 bg-soft-blue h-100">
                                <v-icon color="info" size="large" class="mb-2">mdi-office-building-marker</v-icon>
                                <div>
                                    <div class="font-weight-bold">Ficha Laboral</div>
                                    <div class="text-caption">Cargo: {{ employee.position }}</div>
                                    <div class="text-caption">Dpto: {{ employee.department }}</div>
                                    <div class="text-caption">Ingreso: {{ employee.hire_date }}</div>
                                </div>
                            </v-card>
                        </v-col>
                    </v-row>
                </v-card-text>
            </v-card>

            <v-card class="rounded-lg elevation-2">
                <v-card-title class="d-flex justify-space-between align-center px-4 pt-4">
                    <span>Historial de Mis Recibos</span>
                    <v-text-field v-model="searchPay" prepend-inner-icon="mdi-magnify" label="Buscar por periodo o monto..." hide-details density="compact" variant="solo-filled" style="max-width: 250px;"></v-text-field>
                </v-card-title>
                <v-data-table :headers="payHeaders" :items="payrolls" :loading="loadingPay" :search="searchPay" density="compact">
                    <template v-slot:item.period="{ item }">
                        {{ item.period_month }}/{{ item.period_year }}
                    </template>
                    <template v-slot:item.net_salary="{ item }">
                        $ {{ item.net_salary }}
                    </template>
                    <template v-slot:item.action="{ item }">
                        <v-btn icon="mdi-file-pdf-box" size="small" color="error" variant="text" @click="downloadPayStub(item)"></v-btn>
                    </template>
                    <template v-slot:no-data>
                        No se han generado recibos de pago para tu perfil aún.
                    </template>
                </v-data-table>
            </v-card>
        </template>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { formatDate } from '@/utils/format';
import { generateWorkLetter, generatePayStub } from '@/utils/reports';

const authStore = useAuthStore();
const employee = ref(null);
const payrolls = ref([]);
const searchPay = ref('');
const loading = ref(true);
const loadingPay = ref(false);
const exporting = ref(false);

const payHeaders = [
    { title: 'Mes/Año', key: 'period' },
    { title: 'Neto Cobrado', key: 'net_salary' },
    { title: 'Recibo PDF', key: 'action', align: 'end', sortable: false }
];

const getRoleLabel = (role) => {
    switch(role) {
        case 'admin': return 'Administrador';
        case 'evaluator': return 'Evaluador';
        case 'support': return 'Soporte';
        case 'technician': return 'Técnico';
        default: return 'Usuario';
    }
};

const loadProfileData = async () => {
    loading.value = true;
    try {
        employee.value = await api.get('employees/me/');
        if (employee.value) {
            loadMyPayrolls();
        }
    } catch (e) {
        console.warn('Este usuario no tiene perfil de empleado vinculado');
    } finally {
        loading.value = false;
    }
};

const loadMyPayrolls = async () => {
    loadingPay.value = true;
    try {
        payrolls.value = await api.get('payroll/me/');
    } catch (e) {
        console.error(e);
    } finally {
        loadingPay.value = false;
    }
};

const downloadWorkLetter = async () => {
    exporting.value = true;
    await generateWorkLetter(employee.value);
    exporting.value = false;
};

const downloadPayStub = async (pay) => {
    await generatePayStub(pay, employee.value);
};

onMounted(loadProfileData);
</script>

<style scoped>
.bg-soft-purple { background-color: #F3E5F5; }
.bg-soft-blue { background-color: #E3F2FD; }
</style>
