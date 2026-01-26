<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Control de Calidad y Auditoría</h1>
        <p class="text-subtitle-1 text-grey">Supervisión de desempeño para Atención al Cliente y Técnicos de Campo</p>
      </v-col>
    </v-row>

    <!-- STATS SUMMARY -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card color="primary" variant="tonal" class="rounded-xl pa-4">
          <div class="text-overline">Pendientes de Auditar</div>
          <div class="text-h4 font-weight-bold">{{ pendingIncidents.length }}</div>
          <div class="text-caption">Incidentes solucionados sin evaluación</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="success" variant="tonal" class="rounded-xl pa-4">
          <div class="text-overline">Auditados este Mes</div>
          <div class="text-h4 font-weight-bold">{{ auditedCount }}</div>
          <div class="text-caption">Cumplimiento de meta: 92%</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- INCIDENT LIST -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="rounded-xl">
          <v-data-table
            :headers="headers"
            :items="pendingIncidents"
            :loading="loading"
            class="elevation-0"
          >
            <template v-slot:item.technician="{ item }">
              <v-chip size="small" variant="outlined" color="secondary" prepend-icon="mdi-account-wrench">
                {{ item.assigned_to_name }}
              </v-chip>
            </template>
            <template v-slot:item.solved_date="{ item }">
              {{ new Date(item.solved_date).toLocaleString() }}
            </template>
            <template v-slot:item.times="{ item }">
                <div class="text-caption">
                    <v-icon size="x-small" color="info">mdi-clock-fast</v-icon> Asig: {{ formatDuration(calcAssign(item)) }}<br>
                    <v-icon size="x-small" color="success">mdi-check-decagram</v-icon> Res: {{ formatDuration(calcRes(item)) }}
                </div>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn color="primary" size="small" prepend-icon="mdi-file-eye" @click="openAudit(item)">Auditar</v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- AUDIT DIALOG -->
    <v-dialog v-model="dialog" max-width="700" persistent>
        <v-card v-if="selected" class="rounded-xl overflow-hidden">
            <v-card-title class="pa-4 bg-primary text-white d-flex justify-space-between align-center">
                <span>Auditoría de Incidencia #{{ selected.id }}</span>
                <v-btn icon="mdi-close" variant="text" @click="dialog = false"></v-btn>
            </v-card-title>
            
            <v-card-text class="pa-6">
                <div class="mb-6 pa-4 bg-grey-lighten-4 rounded-lg">
                    <div class="text-subtitle-2 text-primary font-weight-bold mb-1">DETALLE DEL CASO</div>
                    <div class="text-h6 mb-2">{{ selected.title }}</div>
                    <div class="text-body-2 mb-4">{{ selected.description }}</div>
                    <v-divider class="mb-4"></v-divider>
                    <v-row dense>
                        <v-col cols="6"><span class="text-caption grey--text">Soporte:</span> {{ selected.created_by_name }}</v-col>
                        <v-col cols="6"><span class="text-caption grey--text">Técnico:</span> {{ selected.assigned_to_name }}</v-col>
                    </v-row>
                </div>

                <v-form @submit.prevent="submitAudit" id="auditForm">
                    <v-row>
                        <v-col cols="12" md="6">
                            <div class="d-flex justify-space-between mb-2">
                                <label class="text-subtitle-2 font-weight-bold">Puntaje Soporte (Atención)</label>
                                <span :class="getScoreColor(audit.support_score) + '--text font-weight-bold'">{{ audit.support_score }}/100</span>
                            </div>
                            <v-slider v-model="audit.support_score" color="info" min="1" max="100" thumb-label hide-details></v-slider>
                            <div class="text-caption text-grey mt-1">Evalúa el tiempo de respuesta y trato inicial.</div>
                        </v-col>
                        
                        <v-col cols="12" md="6">
                            <div class="d-flex justify-space-between mb-2">
                                <label class="text-subtitle-2 font-weight-bold">Puntaje Técnico (Resolución)</label>
                                <span :class="getScoreColor(audit.technician_score) + '--text font-weight-bold'">{{ audit.technician_score }}/100</span>
                            </div>
                            <v-slider v-model="audit.technician_score" color="success" min="1" max="100" thumb-label hide-details></v-slider>
                            <div class="text-caption text-grey mt-1">Evalúa la calidad del trabajo y tiempo de cierre.</div>
                        </v-col>

                        <v-col cols="12">
                            <v-textarea
                                v-model="audit.comments"
                                label="Observaciones de Control de Calidad"
                                variant="outlined"
                                rows="2"
                                placeholder="Escribe aquí el análisis de la gestión..."
                                required
                            ></v-textarea>
                        </v-col>

                        <v-col cols="12">
                            <v-divider class="mb-4"></v-divider>
                            <div class="d-flex align-center">
                                <v-icon color="success" class="mr-2">mdi-cash-check</v-icon>
                                <div>
                                    <div class="text-subtitle-2 font-weight-bold">Sugerir Bono Extraordinario</div>
                                    <div class="text-caption text-grey">Por resolución destacada o atención heroica</div>
                                </div>
                                <v-spacer></v-spacer>
                                <v-text-field
                                    v-model="audit.suggested_bonus"
                                    label="Monto ($)"
                                    prefix="$"
                                    type="number"
                                    density="compact"
                                    variant="outlined"
                                    style="max-width: 150px;"
                                    hide-details
                                ></v-text-field>
                            </div>
                        </v-col>
                    </v-row>
                </v-form>
            </v-card-text>

            <v-card-actions class="pa-4 bg-grey-lighten-5">
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
                <v-btn color="primary" size="large" type="submit" form="auditForm" :loading="saving" prepend-icon="mdi-check-decagram"> Finalizar Auditoría </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';

const loading = ref(true);
const incidents = ref([]);
const auditHistory = ref([]);
const dialog = ref(false);
const selected = ref(null);
const saving = ref(false);

const audit = ref({
    support_score: 80,
    technician_score: 80,
    comments: '',
    suggested_bonus: 0
});

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Asunto', key: 'title' },
  { title: 'Cierre', key: 'solved_date' },
  { title: 'Tiempos (Snapshot)', key: 'times', sortable: false },
  { title: 'Personal Responsable', key: 'technician' },
  { title: 'Acción', key: 'actions', sortable: false, align: 'center' },
];

const pendingIncidents = computed(() => {
    // Solo incidentes solucionados que no tengan auditoria linkeada (simulado por filtro local si el backend no trae link)
    // En el futuro el backend debería filtrar esto.
    return incidents.value.filter(inc => inc.status === 'solved' && !auditHistory.value.some(a => a.incident === inc.id));
});

const auditedCount = computed(() => auditHistory.value.length);

const loadData = async () => {
  loading.value = true;
  try {
    const [incRes, auditRes] = await Promise.all([
      api.get('incidents/'),
      api.get('incident-audits/')
    ]);
    incidents.value = incRes;
    auditHistory.value = auditRes;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const openAudit = (item) => {
    selected.value = item;
    audit.value = { support_score: 80, technician_score: 80, comments: '', suggested_bonus: 0 };
    dialog.value = true;
};

const submitAudit = async () => {
    saving.value = true;
    try {
        await api.post('incident-audits/', {
            incident: selected.value.id,
            ...audit.value
        });
        dialog.value = false;
        loadData();
    } catch (e) {
        alert('Error al guardar auditoría');
    } finally {
        saving.value = false;
    }
};

// HELPERS
const calcAssign = (inc) => {
    if (!inc.assigned_at) return 0;
    return (new Date(inc.assigned_at) - new Date(inc.start_date)) / 1000;
};
const calcRes = (inc) => {
    if (!inc.solved_date || !inc.assigned_at) return 0;
    return (new Date(inc.solved_date) - new Date(inc.assigned_at)) / 1000;
};
const formatDuration = (s) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    return `${h}h ${m}m`;
};
const getScoreColor = (s) => (s >= 80 ? 'success' : (s >= 60 ? 'warning' : 'error'));

onMounted(loadData);
</script>
