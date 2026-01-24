<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" app v-if="authStore.isAuthenticated">
      <v-list dense>
        <v-list-item title="Menu Principal" subtitle="Sistema de Incidencias"></v-list-item>
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
          <v-list-item v-if="authStore.isAdmin" prepend-icon="mdi-account-group" title="Usuarios" to="/users"></v-list-item>
        </v-list-group>

        <v-list-group value="HR">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-account-hard-hat" title="RRHH"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-account-card-details" title="Empleados" to="/employees"></v-list-item>
          <v-list-item prepend-icon="mdi-cash-multiple" title="Nómina" to="/payroll"></v-list-item>
        </v-list-group>

        <v-list-item v-if="authStore.user?.role === 'admin'" prepend-icon="mdi-shield-history" title="Auditoría" to="/audit"></v-list-item>

        <v-list-group value="FieldService">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-truck-check" title="Field Service"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-clipboard-list-outline" title="Órdenes de Trabajo" to="/work-orders"></v-list-item>
        </v-list-group>

        <v-list-group value="Inventory">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-warehouse" title="Inventario"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-package-variant-closed" title="Repuestos" to="/spare-parts"></v-list-item>
          <v-list-item prepend-icon="mdi-file-document-outline" title="Presupuestos" to="/budgets"></v-list-item>
        </v-list-group>
      </v-list>
      
      <template v-slot:append>
        <div class="pa-2">
          <v-btn block color="error" @click="logout">
            Cerrar Sesión
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar v-if="authStore.isAuthenticated" app color="primary" elevation="1">
      <v-app-bar-nav-icon @click="drawer = !drawer" v-if="authStore.isAuthenticated"></v-app-bar-nav-icon>
      <v-avatar size="42" class="ml-2" rounded="0">
        <v-img src="/logo.png" style="mix-blend-mode: multiply;" alt="NatTelf Logo"></v-img>
      </v-avatar>
      <v-toolbar-title class="font-weight-bold ml-2">NatTelf</v-toolbar-title>
      
      <v-spacer></v-spacer>

      <!-- Notifications -->
      <v-menu v-if="authStore.isAuthenticated" :close-on-content-click="false" location="bottom end">
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props" class="mr-2">
            <v-badge :content="unreadCount" :model-value="unreadCount > 0" color="error">
              <v-icon>mdi-bell</v-icon>
            </v-badge>
          </v-btn>
        </template>
        <v-card width="350">
          <v-list lines="three">
            <v-list-subheader class="d-flex align-center">
              Notificaciones
              <v-spacer></v-spacer>
              <v-btn variant="text" size="x-small" color="primary" @click="readAll">Marcar todo leido</v-btn>
            </v-list-subheader>
            <v-divider></v-divider>
            <v-list-item v-for="notif in notifications" :key="notif.id" :title="notif.title" :class="{'bg-soft-purple': !notif.is_read}" @click="goToNotif(notif)">
                <template v-slot:subtitle>
                    <div class="text-caption text-grey">{{ formatDate(notif.created_at) }}</div>
                    <div>{{ notif.message }}</div>
                </template>
                <template v-slot:prepend>
                    <v-icon :color="notif.is_read ? 'grey' : 'primary'">mdi-circle-small</v-icon>
                </template>
            </v-list-item>
            <v-list-item v-if="notifications.length === 0" title="Sin notificaciones"></v-list-item>
          </v-list>
        </v-card>
      </v-menu>

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
              <v-divider class="my-3"></v-divider>
              <v-btn rounded variant="text" prepend-icon="mdi-logout" color="error" block @click="logout">
                Cerrar Sesión
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-menu>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import api from '@/services/api';

const drawer = ref(false);
const authStore = useAuthStore();
const router = useRouter();

const logout = () => {
  authStore.logout();
  router.push('/login');
};
const notifications = ref([]);
const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length);

const fetchNotifications = async () => {
  if (authStore.isAuthenticated) {
    try {
      notifications.value = await api.get('notifications/');
    } catch (e) {
      console.error(e);
    }
  }
};

const readAll = async () => {
  await api.post('notifications/mark_all_read/');
  fetchNotifications();
};

const goToNotif = async (notif) => {
  if (!notif.is_read) {
    await api.patch(`notifications/${notif.id}/`, { is_read: true });
  }
  if (notif.link) router.push(notif.link);
  fetchNotifications();
};

onMounted(() => {
  fetchNotifications();
  // Poll every 60s
  setInterval(fetchNotifications, 60000);
});
</script>

<style scoped>
.bg-soft-purple {
    background-color: #F3E5F5;
}
</style>
