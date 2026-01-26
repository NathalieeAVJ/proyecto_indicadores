<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12" class="d-flex justify-space-between align-center">
        <h1 class="text-h4 font-weight-bold">Indicadores de Rendimiento (KPIs)</h1>
        <v-btn icon="mdi-refresh" @click="loadData" :loading="loading" variant="text"></v-btn>
      </v-col>
    </v-row>

    <!-- KPI Cards -->
    <v-row v-if="stats">
      <v-col cols="12" md="3">
        <v-card class="rounded-xl elevation-2 border-primary border-sm">
          <v-card-text class="text-center pa-6">
            <v-icon color="primary" size="48" class="mb-2">mdi-clock-fast</v-icon>
            <div class="text-h3 font-weight-bold">{{ formatSeconds(stats.phone.avg_assignment_time) }}</div>
            <div class="text-subtitle-1 text-grey">T. Promedio Asignación (Tel)</div>
            <div class="text-caption">Meta: < 15 min</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="rounded-xl elevation-2 border-secondary border-sm">
          <v-card-text class="text-center pa-6">
            <v-icon color="secondary" size="48" class="mb-2">mdi-account-clock</v-icon>
            <div class="text-h3 font-weight-bold">{{ formatSeconds(stats.phone.avg_resolution_time) }}</div>
            <div class="text-subtitle-1 text-grey">T. Promedio Resolución (Tel)</div>
            <div class="text-caption">Eficiencia del Técnico</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="rounded-xl elevation-2 border-info border-sm">
          <v-card-text class="text-center pa-6">
            <v-icon color="info" size="48" class="mb-2">mdi-antenna</v-icon>
            <div class="text-h3 font-weight-bold">{{ formatSeconds(stats.radiobase.avg_resolution_time) }}</div>
            <div class="text-subtitle-1 text-grey">T. Promedio Res. (Radiobase)</div>
            <div class="text-caption">Complejidad Técnica Alta</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="rounded-xl elevation-2 border-success border-sm">
          <v-card-text class="text-center pa-6">
            <v-icon color="success" size="48" class="mb-2">mdi-check-decagram</v-icon>
            <div class="text-h3 font-weight-bold">{{ stats.summary.total_general_incidents }}</div>
            <div class="text-subtitle-1 text-grey">Total Incidencias Atendidas</div>
            <div class="text-caption">Volumen total de carga</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Row -->
    <v-row class="mt-6" v-if="stats">
      <v-col cols="12" md="6">
        <v-card title="Eficiencia por Técnico (Tiempo Promedio)" class="rounded-lg">
          <v-card-text>
            <div style="height: 300px;">
              <Bar :data="techChartConfig.data" :options="techChartConfig.options" />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card title="Distribución por Tipo de Falla" class="rounded-lg">
          <v-card-text>
            <div style="height: 300px;">
              <Doughnut :data="typeChartConfig.data" :options="typeChartConfig.options" />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';
import { Bar, Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement);

const loading = ref(true);
const stats = ref(null);

const formatSeconds = (s) => {
  if (!s) return 'N/A';
  const hours = Math.floor(s / 3600);
  const minutes = Math.floor((s % 3600) / 60);
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
};

const loadData = async () => {
  loading.value = true;
  try {
    stats.value = await api.get('incidents/statistics/');
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const router = useRouter();

const techChartConfig = computed(() => {
  if (!stats.value) return { data: { datasets: [] } };
  
  const phoneTechs = stats.value.phone.technician_performance;
  return {
    data: {
      labels: phoneTechs.map(t => t.full_name),
      datasets: [
        {
          label: 'Horas Promedio',
          backgroundColor: '#9575CD',
          data: phoneTechs.map(t => (t.avg_seconds / 3600).toFixed(2))
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (evt, elements, chart) => {
        if (elements.length > 0) {
            const index = elements[0].index;
            const tech = phoneTechs[index];
            if (tech && tech.id) {
                // El link debe ir al perfil del empleado. No al User ID. 
                // Pero mis IDs en tech_performance son de User. 
                // Necesito asegurar que sea el ID de Employee.
                router.push(`/employees/${tech.id}`);
            }
        }
      },
      plugins: { 
        legend: { display: false },
        tooltip: {
            callbacks: {
                afterLabel: (context) => `Total Solucionadas: ${phoneTechs[context.dataIndex].total_solved}`
            }
        }
      },
      scales: { y: { title: { display: true, text: 'Horas' } } }
    }
  };
});

const typeChartConfig = computed(() => {
  if (!stats.value) return { data: { datasets: [] } };
  
  const types = stats.value.phone.by_type;
  return {
    data: {
      labels: types.map(t => t.failure_type__name || 'Otros'),
      datasets: [
        {
          backgroundColor: ['#42A5F5', '#66BB6A', '#FFA726', '#EF5350', '#AB47BC'],
          data: types.map(t => t.count)
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  };
});

onMounted(loadData);
</script>
