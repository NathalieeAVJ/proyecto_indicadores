<template>
  <v-menu :close-on-content-click="false" location="bottom end" v-model="menuOpen">
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
          <v-btn variant="text" size="x-small" color="primary" @click="readAll" :disabled="unreadCount === 0">
            Marcar todo leido
          </v-btn>
        </v-list-subheader>
        <v-divider></v-divider>
        
        <v-list-item v-if="loadingList" class="text-center">
             <v-progress-circular indeterminate size="24" color="primary"></v-progress-circular>
        </v-list-item>

        <template v-else>
            <v-list-item 
                v-for="notif in notifications" 
                :key="notif.id" 
                :title="notif.title" 
                :class="{'bg-soft-purple': !notif.is_read}" 
                @click="goToNotif(notif)"
                class="cursor-pointer"
            >
                <template v-slot:subtitle>
                    <div class="text-caption text-grey">{{ formatDate(notif.created_at) }}</div>
                    <div>{{ notif.message }}</div>
                </template>
                <template v-slot:prepend>
                    <v-icon :color="notif.is_read ? 'grey' : 'primary'">
                        {{ notif.is_read ? 'mdi-check' : 'mdi-circle-small' }}
                    </v-icon>
                </template>
            </v-list-item>
            <v-list-item v-if="notifications.length === 0" title="Sin notificaciones nuevas" class="text-center text-medium-emphasis mb-2"></v-list-item>
        </template>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const menuOpen = ref(false);
const unreadCount = ref(0);
const notifications = ref([]);
const loadingList = ref(false);
let pollingTimer = null;

// Watch menu state: fetch list when opened
watch(menuOpen, (isOpen) => {
    if (isOpen) {
        fetchNotificationList();
    }
});

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString();
};

const fetchUnreadCount = async () => {
  if (!authStore.isAuthenticated) return;
  try {
     // Expected response: { count: 5 }
     const res = await api.get('notifications/unread_count/');
     unreadCount.value = res.count;
  } catch (e) {
    console.error("Failed to poll notifications", e);
  }
};

const fetchNotificationList = async () => {
    loadingList.value = true;
    try {
        // Fetch custom list or full list? API usually returns paginated or list
        notifications.value = await api.get('notifications/');
        // Sync count just in case
        unreadCount.value = notifications.value.filter(n => !n.is_read).length; 
    } catch (e) {
        console.error(e);
    } finally {
        loadingList.value = false;
    }
};

const readAll = async () => {
  await api.post('notifications/mark_all_read/');
  notifications.value.forEach(n => n.is_read = true);
  unreadCount.value = 0;
};

const goToNotif = async (notif) => {
  if (!notif.is_read) {
    await api.patch(`notifications/${notif.id}/`, { is_read: true });
    notif.is_read = true;
    unreadCount.value = Math.max(0, unreadCount.value - 1);
  }
  menuOpen.value = false;
  if (notif.link) {
    router.push(notif.link);
  }
};

onMounted(() => {
  // Initial fetch
  fetchUnreadCount();
  // Poll every 30 seconds
  pollingTimer = setInterval(fetchUnreadCount, 30000);
});

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer);
});
</script>

<style scoped>
.bg-soft-purple {
    background-color: #F3E5F5;
}
.cursor-pointer {
    cursor: pointer;
}
</style>
