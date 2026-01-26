<template>
  <v-container fluid class="pa-6">
    <!-- Standard System Breadcrumbs -->
    <v-breadcrumbs 
      :items="[
        { title: 'Dashboard', disabled: false, to: '/' },
        { title: 'RRHH', disabled: true },
        { title: 'Organigrama', disabled: true }
      ]"
      class="pa-0 mb-4"
    >
      <template v-slot:divider>
        <v-icon icon="mdi-chevron-right"></v-icon>
      </template>
    </v-breadcrumbs>

    <!-- Standard System Header -->
    <v-row class="mb-6 align-center">
      <v-col cols="12" md="8">
        <h1 class="text-h3 font-weight-bold text-primary mb-2">Estructura Organizativa</h1>
        <p class="text-subtitle-1 text-grey-darken-1">NatTelf: Organigrama Institucional por Departamentos</p>
      </v-col>
      <v-col cols="12" md="4" class="text-right">
        <v-btn color="primary" variant="outlined" prepend-icon="mdi-refresh" @click="fetchData" :loading="loading">Actualizar</v-btn>
      </v-col>
    </v-row>

    <div v-if="loading" class="d-flex justify-center align-center" style="height: 400px;">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <!-- Striking Diagram Viewport -->
    <div v-else class="org-chart-container pa-4">
      <v-row justify="center">
        <v-col cols="12" class="d-flex flex-column align-center">
          <div v-for="rootDep in rootDepartments" :key="rootDep.id" class="tree-root">
            <OrgNode :node="rootDep" :all-deps="departments" @select="showDetail" />
          </div>
        </v-col>
      </v-row>
    </div>

    <!-- DETAILS DIALOG (Professional/striking) -->
    <v-dialog v-model="dialog" max-width="800" transition="dialog-bottom-transition">
      <v-card v-if="selectedDep" class="rounded-xl overflow-hidden elevation-24">
        <!-- Modal Header with Striking Gradient -->
        <v-toolbar :style="{ background: getEliteGradient(selectedDep.manager_detail?.rank) }" flat height="80">
          <v-container class="d-flex align-center">
            <v-icon size="40" color="white" class="mr-4">
              {{ getRankIcon(selectedDep.manager_detail?.rank) }}
            </v-icon>
            <div>
              <v-toolbar-title class="text-h5 white--text font-weight-black">
                {{ selectedDep.name }}
              </v-toolbar-title>
            </div>
            <v-spacer></v-spacer>
            <v-btn icon="mdi-close" variant="text" @click="dialog = false" color="white"></v-btn>
          </v-container>
        </v-toolbar>

        <v-card-text class="pa-8 pb-10 bg-white">
          <v-row>
            <v-col cols="12" md="5">
              <div class="leader-spotlight rounded-xl pa-8 text-center h-100 elevation-2">
                <v-avatar size="140" class="elevation-12 mb-6 border-standard">
                  <v-img v-if="selectedDep.manager_detail" src="https://ui-avatars.com/api/?background=6200EA&color=fff&size=200&name="></v-img>
                  <v-icon v-else size="100" color="grey-lighten-4">mdi-account-circle</v-icon>
                </v-avatar>
                
                <h3 class="text-h5 font-weight-black color-navy mb-1">
                  {{ selectedDep.manager_detail?.full_name || 'Sin Asignar' }}
                </h3>
                <v-chip color="primary" variant="tonal" class="mb-8 font-weight-bold">
                  {{ selectedDep.manager_detail?.position || 'Responsable de Area' }}
                </v-chip>
                
                <div class="text-left mission-box pa-4 rounded-lg">
                  <div class="text-overline font-weight-bold text-primary mb-1">FUNCIÓN</div>
                  <p class="text-body-2 text-grey-darken-3 italic">{{ selectedDep.description || 'Departamento estratégico de NatTelf.' }}</p>
                </div>
              </div>
            </v-col>

            <v-col cols="12" md="7">
              <div class="d-flex align-center mb-4">
                <v-icon color="indigo-darken-2" class="mr-2">mdi-account-group</v-icon>
                <h3 class="text-h6 font-weight-black">Personal ({{ selectedDep.staff_count }})</h3>
              </div>
              
              <div class="staff-scroller">
                <v-list density="comfortable" class="bg-transparent pa-0">
                  <v-list-item 
                    v-for="person in selectedDep.staff_list" 
                    :key="person.id" 
                    :to="`/employees/${person.id}`"
                    class="rounded-lg mb-2 border-thin"
                    variant="flat"
                  >
                    <template v-slot:prepend>
                      <v-avatar color="indigo-lighten-4" size="40" class="mr-3">
                        <span class="text-body-2 font-weight-bold text-indigo-darken-4">{{ person.full_name[0] }}</span>
                      </v-avatar>
                    </template>
                    <v-list-item-title class="font-weight-bold">{{ person.full_name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ person.position }}</v-list-item-subtitle>
                    <template v-slot:append>
                      <v-chip size="x-small" :color="person.status === 'active' ? 'success' : 'warning'" variant="flat">
                        {{ person.status.toUpperCase() }}
                      </v-chip>
                    </template>
                  </v-list-item>
                </v-list>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import OrgNode from '@/components/OrgNode.vue';

const router = useRouter();
const departments = ref([]);
const loading = ref(true);
const dialog = ref(false);
const selectedDep = ref(null);

const rootDepartments = computed(() => departments.value.filter(d => !d.parent));

const fetchData = async () => {
  loading.value = true;
  try {
    departments.value = await api.get('departments/');
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const showDetail = (dep) => {
  selectedDep.value = dep;
  dialog.value = true;
};

const getEliteGradient = (rank) => {
  const map = {
    0: 'linear-gradient(135deg, #1A237E 0%, #6200EA 100%)',
    1: 'linear-gradient(135deg, #01579B 0%, #00B0FF 100%)',
    2: 'linear-gradient(135deg, #1B5E20 0%, #00E676 100%)',
    3: 'linear-gradient(135deg, #E65100 0%, #FF9100 100%)',
    default: 'linear-gradient(135deg, #263238 0%, #78909C 100%)'
  };
  return map[rank] || map.default;
};

const getRankIcon = (rank) => {
  if (rank === 0) return 'mdi-crown';
  if (rank === 1) return 'mdi-layers-triple';
  if (rank === 2) return 'mdi-shield-crown-outline';
  if (rank === 3) return 'mdi-star-face';
  return 'mdi-hexagon-multiple';
};

onMounted(fetchData);
</script>

<style scoped>
.org-chart-container {
  overflow-x: auto;
  min-width: 1000px;
  background: white;
  border-radius: 24px;
  border: 1px solid #E0E0E0;
}

.tree-root {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.leader-spotlight {
  background: #F8F9FA;
  border: 1px solid #ECEFF1;
}

.border-standard {
  border: 4px solid white;
}

.mission-box {
  background: white;
  border: 1px solid #ECEFF1;
}

.staff-scroller {
  max-height: 400px;
  overflow-y: auto;
}

.border-thin {
  border: 1px solid #F5F5F5 !important;
}

.color-navy { color: #1A237E; }
</style>
