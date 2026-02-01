<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 font-weight-bold mb-2">Dashboard Ejecutivo</h1>
        <p class="text-subtitle-1 text-medium-emphasis">Resumen de operaciones en tiempo real</p>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="loading">
      <v-col cols="12" md="4" v-for="n in 3" :key="n">
        <v-skeleton-loader type="card"></v-skeleton-loader>
      </v-col>
    </v-row>

    <!-- Stats Cards -->
    <v-row v-else>
      <!-- Incidencias -->
      <v-col cols="12" md="4">
        <v-card class="mx-auto" elevation="2" rounded="lg">
          <v-card-item>
            <template v-slot:prepend>
              <v-icon icon="mdi-alert-circle-outline" color="error" size="x-large"></v-icon>
            </template>
            <v-card-title class="text-h5">Incidencias Abiertas</v-card-title>
            <v-card-subtitle>Pendientes + En Revisión</v-card-subtitle>
          </v-card-item>
          <v-card-text class="py-0">
            <div class="text-h2 font-weight-bold text-error">
              {{ stats.incidents_open }}
            </div>
          </v-card-text>
          <v-card-actions>
            <v-btn variant="text" color="error" :to="{ path: '/incidents/list' }">Ver detalles</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Ventas -->
      <v-col cols="12" md="4">
        <v-card class="mx-auto" elevation="2" rounded="lg">
          <v-card-item>
            <template v-slot:prepend>
              <v-icon icon="mdi-cash-multiple" color="success" size="x-large"></v-icon>
            </template>
            <v-card-title class="text-h5">Ventas del Mes</v-card-title>
            <v-card-subtitle>Total acumulado</v-card-subtitle>
          </v-card-item>
          <v-card-text class="py-0">
            <div class="text-h2 font-weight-bold text-success">
              ${{ formatCurrency(stats.monthly_sales) }}
            </div>
          </v-card-text>
          <v-card-actions>
            <v-btn variant="text" color="success" :to="{ path: '/ventas/list' }">Ver reporte</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Inventario -->
      <v-col cols="12" md="4">
        <v-card class="mx-auto" elevation="2" rounded="lg">
          <v-card-item>
            <template v-slot:prepend>
              <v-icon icon="mdi-package-variant-closed-alert" color="warning" size="x-large"></v-icon>
            </template>
            <v-card-title class="text-h5">Stock Bajo</v-card-title>
            <v-card-subtitle>Alertas de Inventario</v-card-subtitle>
          </v-card-item>
          <v-card-text class="py-0">
            <div class="text-h2 font-weight-bold text-warning">
              {{ stats.low_stock_items }}
            </div>
          </v-card-text>
          <v-card-actions>
            <v-btn variant="text" color="warning" :to="{ path: '/spare-parts/list' }">Reabastecer</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DashboardService from '@/services/DashboardService'

const loading = ref(true)
const stats = ref({
  incidents_open: 0,
  monthly_sales: 0,
  low_stock_items: 0
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 2 }).format(value)
}

const fetchStats = async () => {
  try {
    loading.value = true
    const response = await DashboardService.getSummaryStats()
    stats.value = response.data
  } catch (error) {
    console.error('Error fetching dashboard stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>
