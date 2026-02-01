<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" app v-if="authStore.isAuthenticated">
      <v-list dense>
        <v-list-item prepend-icon="mdi-apps" title="Menu Principal" subtitle="Sistema de Incidencias"></v-list-item>
        <v-divider></v-divider>

        <v-list-item prepend-icon="mdi-view-dashboard" title="Dashboard" to="/"></v-list-item>
        
        <v-list-group value="Management">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-folder" title="Gestión"></v-list-item>
          </template>
          
          <v-list-item prepend-icon="mdi-alert-circle" title="Incidencias (Tel)" to="/incidents"></v-list-item>
          <v-list-item prepend-icon="mdi-antenna" title="Tickets (Radios)" to="/rb-incidents"></v-list-item>
          <v-list-item prepend-icon="mdi-phone" title="Números" to="/phones"></v-list-item>
          <v-list-item prepend-icon="mdi-tower-fire" title="Radiobases" to="/radio-bases"></v-list-item>
          <v-list-item prepend-icon="mdi-hammer-wrench" title="Tipos de Falla" to="/failure-types"></v-list-item>
          <v-list-item v-if="authStore.isAdmin" prepend-icon="mdi-account-group" title="Usuarios" to="/users"></v-list-item>
        </v-list-group>

        <v-list-group value="HR">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-account-hard-hat" title="RRHH"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-account-group" title="Empleados" to="/employees"></v-list-item>
          <v-list-item prepend-icon="mdi-sitemap" title="Departamentos" to="/departments"></v-list-item>
          <v-list-item prepend-icon="mdi-account-network" title="Organigrama" to="/departments/org-chart"></v-list-item>
          <v-list-item prepend-icon="mdi-account-off" title="Lista Negra" to="/rrhh/blacklist"></v-list-item>
          <v-list-item prepend-icon="mdi-cash-multiple" title="Nómina" to="/payroll"></v-list-item>
          <v-list-item v-if="authStore.isAdmin || authStore.user?.role === 'evaluator' || authStore.user?.role === 'admin'" prepend-icon="mdi-check-decagram" title="Aprobaciones" to="/approvals"></v-list-item>
        </v-list-group>


        <v-list-group value="FieldService">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-truck-check" title="Field Service"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-clipboard-list-outline" title="Órdenes de Trabajo" to="/work-orders"></v-list-item>
        </v-list-group>

        <v-list-group value="Logistics">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-dolly" title="Logística"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-car-cog" title="Gestión de Flota" to="/logistica/fleet"></v-list-item>
        </v-list-group>

        <v-list-group value="Knowledge">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-book-open-variant" title="Conocimiento"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-library-shelves" title="Wiki Técnica" to="/wiki"></v-list-item>
          <v-list-item prepend-icon="mdi-folder-file" title="Gestión Documental" to="/documentos"></v-list-item>
        </v-list-group>

        <v-list-group value="Procurement">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-handshake" title="Procura"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-office-building" title="Proveedores" to="/procura/suppliers"></v-list-item>
        </v-list-group>

        <v-list-group value="Sales">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-cart-check" title="Ventas"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-sim" title="SIM / eSIM" to="/ventas"></v-list-item>
        </v-list-group>

        <v-list-group value="Inventory">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-warehouse" title="Inventario"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-package-variant-closed" title="Repuestos" to="/spare-parts"></v-list-item>
          <v-list-item prepend-icon="mdi-laptop-account" title="Activos y Equipos" to="/inventory/assets"></v-list-item>
          <v-list-item prepend-icon="mdi-file-document-outline" title="Presupuestos" to="/budgets"></v-list-item>
        </v-list-group>

        <v-list-group value="Analytics">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-chart-line" title="Analíticas"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-gauge" title="Rendimiento KPI" to="/analytics/performance"></v-list-item>
          <v-list-item v-if="authStore.isAdmin || authStore.user?.role === 'evaluator'" prepend-icon="mdi-shield-check" title="Auditoría de Servicio" to="/auditor"></v-list-item>
        </v-list-group>

        <v-list-item v-if="authStore.user?.role === 'admin'" prepend-icon="mdi-shield-search" title="Logs de Auditoría" to="/audit"></v-list-item>
        <v-divider class="my-2"></v-divider>
        <v-list-item prepend-icon="mdi-help-circle" title="Manual de Usuario" to="/help/manual" color="secondary"></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar v-if="authStore.isAuthenticated" app color="primary" elevation="1">
      <v-app-bar-nav-icon @click="drawer = !drawer" v-if="authStore.isAuthenticated"></v-app-bar-nav-icon>
      <v-avatar size="42" class="ml-2" rounded="0">
        <v-img src="/logo.png" style="mix-blend-mode: multiply;" alt="NatTelf Logo"></v-img>
      </v-avatar>
      <v-toolbar-title class="font-weight-bold ml-2">NatTelf</v-toolbar-title>
      
      <v-spacer></v-spacer>

      <!-- Notifications -->
      <!-- Notifications -->
      <NotificationBell v-if="authStore.isAuthenticated" />

      <v-menu v-if="authStore.isAuthenticated" min-width="200px" rounded>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props" class="mr-2">
            <v-avatar color="secondary" size="40">
              <v-icon color="white">mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        <v-card>
          <v-card-text>
            <div class="mx-auto text-center">
              <v-avatar color="secondary">
                <v-icon color="white">mdi-account</v-icon>
              </v-avatar>
              <h3 class="mt-2">{{ authStore.user?.username }}</h3>
              <p class="text-caption mt-1">{{ authStore.user?.email }}</p>
              <v-divider class="my-3"></v-divider>
              <v-btn rounded variant="text" prepend-icon="mdi-account-circle-outline" block to="/users/me">
                Mi Perfil
              </v-btn>
              <v-btn rounded variant="text" prepend-icon="mdi-account-details" block color="secondary" to="/self-service">
                Mis Trámites
              </v-btn>
              <v-divider class="my-3"></v-divider>
              <v-btn rounded variant="text" prepend-icon="mdi-logout" color="error" block @click="logout">
                Cerrar Sesión
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-menu>
    </v-app-bar>

    <!-- SESSION TIMEOUT WARNING DIALOG -->
    <v-dialog v-model="sessionDialog" max-width="450" persistent>
        <v-card class="rounded-lg border-error border-sm">
            <v-card-title class="bg-error text-white d-flex align-center pa-4">
                <v-icon class="mr-2">mdi-timer-alert</v-icon>
                Su sesión está por expirar
            </v-card-title>
            <v-card-text class="pa-6 text-center">
                <p class="text-body-1 mb-4">
                    Por seguridad, su sesión se cerrará automáticamente en 2 minutos debido al tiempo transcurrido (1 hora).
                </p>
                <div class="text-h6 font-weight-bold color-error mb-2">
                    ¿Desea extender su sesión una hora más?
                </div>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions class="pa-4">
                <v-btn color="grey" variant="text" @click="logout" prepend-icon="mdi-logout">No, salir</v-btn>
                <v-spacer></v-spacer>
                <v-btn color="primary" variant="elevated" @click="extendSession" prepend-icon="mdi-clock-check">Sí, seguir trabajando</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import NotificationBell from '@/components/NotificationBell.vue';

const drawer = ref(false);
const authStore = useAuthStore();
const router = useRouter();

// Watch for authentication changes to start/stop the timer
watch(() => authStore.isAuthenticated, (newVal) => {
  if (newVal) {
    startSessionTimer();
  } else {
    clearTimeout(warningTimer);
    clearTimeout(autoLogoutTimer);
  }
});

// SESSION TIMEOUT LOGIC
const sessionDialog = ref(false);
let warningTimer = null;
let autoLogoutTimer = null;

const startSessionTimer = () => {
  clearTimeout(warningTimer);
  clearTimeout(autoLogoutTimer);
  
  if (authStore.isAuthenticated) {
    // 1 hour timer for warning (3600000 ms)
    warningTimer = setTimeout(() => {
      showSessionWarning();
    }, 3600000); 
  }
};

const showSessionWarning = () => {
  sessionDialog.value = true;
  // 2 minutes to respond (120000 ms)
  autoLogoutTimer = setTimeout(() => {
    if (sessionDialog.value) {
      logout();
    }
  }, 120000);
};

const extendSession = () => {
  sessionDialog.value = false;
  startSessionTimer();
};

const logout = () => {
  clearTimeout(warningTimer);
  clearTimeout(autoLogoutTimer);
  sessionDialog.value = false;
  authStore.logout();
  router.push('/login');
};

onMounted(() => {
  startSessionTimer();
});
</script>

<style scoped>
.bg-soft-purple {
    background-color: #F3E5F5;
}
</style>
