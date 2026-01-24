<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Dashboard de Gestión</h1>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="4">
        <v-text-field v-model="startDate" type="date" label="Desde" @change="fetchData"></v-text-field>
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field v-model="endDate" type="date" label="Hasta" @change="fetchData"></v-text-field>
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center">
        <v-btn color="secondary" @click="resetFilters">Limpiar Filtros</v-btn>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
    </v-row>

    <v-row v-else>
      <!-- Summary Cards -->
      <v-col cols="12" md="3">
         <v-card color="primary" dark elevation="2">
           <v-card-text class="pa-4">
             <div class="text-subtitle-1">Total General</div>
             <div class="text-h4 font-weight-bold">{{ stats.summary?.total_general_incidents }}</div>
           </v-card-text>
         </v-card>
      </v-col>
      <v-col cols="12" md="3">
         <v-card color="info" dark elevation="2">
           <v-card-text class="pa-4">
             <div class="text-subtitle-1">Incidentes Telefónicos</div>
             <div class="text-h4 font-weight-bold">{{ stats.phone?.total }}</div>
           </v-card-text>
         </v-card>
      </v-col>
      <v-col cols="12" md="3">
         <v-card color="indigo" dark elevation="2">
           <v-card-text class="pa-4">
             <div class="text-subtitle-1">Incidentes Radiobases</div>
             <div class="text-h4 font-weight-bold">{{ stats.radiobase?.total }}</div>
           </v-card-text>
         </v-card>
      </v-col>
      <v-col cols="12" md="3">
         <v-card color="teal" dark elevation="2">
           <v-card-text class="pa-4">
             <div class="text-subtitle-1">Total Trabajadores</div>
             <div class="text-h4 font-weight-bold">{{ stats.rrhh?.total_employees }}</div>
           </v-card-text>
         </v-card>
      </v-col>
      
      <!-- Charts Phone -->
      <v-col cols="12"><h2 class="text-h5 mt-4">Telefonía</h2></v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Estados (Teléfonos)</v-card-title>
          <v-card-text><canvas id="phoneStatusChart"></canvas></v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Tipos de Falla (Teléfonos)</v-card-title>
          <v-card-text><canvas id="phoneTypeChart"></canvas></v-card-text>
        </v-card>
      </v-col>

      <!-- Charts RadioBase -->
      <v-col cols="12"><h2 class="text-h5 mt-4">Infraestructura (Radiobases)</h2></v-col>
      
      <!-- Interactive Map -->
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon start color="primary">mdi-map-marker-radius</v-icon>
            Mapa Operativo de Estaciones
            <v-spacer></v-spacer>
            <div class="text-caption">
                <v-chip size="x-small" color="success" class="mr-1">Operativa</v-chip>
                <v-chip size="x-small" color="error">Con Falla</v-chip>
            </div>
          </v-card-title>
          <v-card-text>
            <div id="map" style="height: 400px; width: 100%; border-radius: 8px;"></div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Estados (Radiobases)</v-card-title>
          <v-card-text><canvas id="rbStatusChart"></canvas></v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Tipos de Falla (Radiobases)</v-card-title>
          <v-card-text><canvas id="rbTypeChart"></canvas></v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import api from '@/services/api';
import Chart from 'chart.js/auto';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with bundlers
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const stats = ref({
    phone: { total: 0, by_status: [], by_type: [] },
    radiobase: { total: 0, by_status: [], by_type: [] },
    summary: { total_general: 0 }
});
const loading = ref(true);
const startDate = ref('');
const endDate = ref('');
let map = null;

let psChart = null;
let ptChart = null;
let rsChart = null;
let rtChart = null;

const statusColors = {
    'pending': '#EF9A9A',
    'in_review': '#FFF59D',
    'solved': '#A5D6A7',
    'postponed': '#BDBDBD'
};
const typeColors = ['#9575CD', '#B39DDB', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA', '#90CAF9', '#CE93D8', '#F48FB1'];

const renderCharts = () => {
    // Cleanup
    if (psChart) psChart.destroy();
    if (ptChart) ptChart.destroy();
    if (rsChart) rsChart.destroy();
    if (rtChart) rtChart.destroy();
    
    if (loading.value) return;

    const createConfig = (data, labels, label, axis = 'x', colors) => ({
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label,
                data,
                backgroundColor: colors || typeColors,
                borderRadius: 4,
            }]
        },
        options: { 
            indexAxis: axis,
            responsive: true, 
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'top', labels: { boxWidth: 10 } }
            },
            scales: {
                y: { beginAtZero: true, grid: { display: false } },
                x: { grid: { display: false } }
            }
        }
    });

    const getStatusColors = (labels) => labels.map(s => statusColors[s] || '#BDBDBD');

    // Phone Charts
    const psCtx = document.getElementById('phoneStatusChart');
    if (psCtx && stats.value.phone?.by_status?.length) {
        const labels = stats.value.phone.by_status.map(x => {
            if (x.status === 'pending') return 'Pendiente';
            if (x.status === 'in_review') return 'En Revisión';
            if (x.status === 'solved') return 'Resuelto';
            return x.status;
        });
        const data = stats.value.phone.by_status.map(x => x.count);
        psChart = new Chart(psCtx, createConfig(data, labels, 'Tickets por Estado', 'x', getStatusColors(stats.value.phone.by_status.map(x => x.status))));
    }
    
    // Phone Type Charts
    const ptCtx = document.getElementById('phoneTypeChart');
    if (ptCtx && stats.value.phone?.by_type?.length) {
        const labels = stats.value.phone.by_type.map(x => x.failure_type__name);
        const data = stats.value.phone.by_type.map(x => x.count);
        ptChart = new Chart(ptCtx, createConfig(data, labels, 'Tickets por Tipo', 'y'));
    }

    // RB Charts
    const rsCtx = document.getElementById('rbStatusChart');
    if (rsCtx && stats.value.radiobase?.by_status?.length) {
        const labels = stats.value.radiobase.by_status.map(x => {
            if (x.status === 'pending') return 'Pendiente';
            if (x.status === 'in_review') return 'En Revisión';
            if (x.status === 'solved') return 'Resuelto';
            return x.status;
        });
        const data = stats.value.radiobase.by_status.map(x => x.count);
        rsChart = new Chart(rsCtx, createConfig(data, labels, 'Tickets RB por Estado', 'x', getStatusColors(stats.value.radiobase.by_status.map(x => x.status))));
    }

    // RB Type Charts
    const rtCtx = document.getElementById('rbTypeChart');
    if (rtCtx && stats.value.radiobase?.by_type?.length) {
        const labels = stats.value.radiobase.by_type.map(x => x.failure_type__name);
        const data = stats.value.radiobase.by_type.map(x => x.count);
        rtChart = new Chart(rtCtx, createConfig(data, labels, 'Tickets RB por Tipo', 'y'));
    }
};

const renderMap = async (data) => {
    if (!data || !Array.isArray(data)) return;
    if (map) {
        map.remove();
        map = null;
    }
    
    await nextTick();
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    map = L.map('map').setView([10.4806, -66.9036], 12); // Focus on Caracas, Venezuela

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    const markers = [];
    data.forEach(rb => {
        if (rb.latitude && rb.longitude) {
            const color = rb.has_active_incident ? '#F44336' : '#4CAF50';
            const markerHtmlStyles = `
                background-color: ${color};
                width: 1.5rem;
                height: 1.5rem;
                display: block;
                left: -0.75rem;
                top: -0.75rem;
                position: relative;
                border-radius: 1.5rem 1.5rem 0;
                transform: rotate(45deg);
                border: 2px solid #FFFFFF;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            `;

            const icon = L.divIcon({
                className: "custom-pin",
                iconAnchor: [0, 24],
                labelAnchor: [-6, 0],
                popupAnchor: [0, -36],
                html: `<span style="${markerHtmlStyles}" />`
            });

            const m = L.marker([rb.latitude, rb.longitude], { icon })
                .bindPopup(`
                    <strong>${rb.name}</strong><br/>
                    Código: ${rb.code}<br/>
                    Estado: ${rb.has_active_incident ? '<span style="color:red">FALLA ACTIVA</span>' : '<span style="color:green">OPERATIVA</span>'}
                `)
                .addTo(map);
            markers.push(m);
        }
    });

    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
};

const fetchData = async () => {
    loading.value = true;
    try {
        let url = 'incidents/statistics/';
        const params = new URLSearchParams();
        if (startDate.value) params.append('start', startDate.value);
        if (endDate.value) params.append('end', endDate.value);
        
        const q = params.toString();
        const [statsRes, mapRes] = await Promise.all([
            api.get(q ? `${url}?${q}` : url),
            api.get('radio-bases/map_data/')
        ]);
        
        stats.value = statsRes;
        loading.value = false;
        
        await nextTick();
        renderCharts();
        renderMap(mapRes);
    } catch (e) {
        console.error(e);
        loading.value = false;
    }
};

const resetFilters = () => {
    startDate.value = '';
    endDate.value = '';
    fetchData();
};

onMounted(fetchData);
</script>


<style scoped>
canvas {
    height: 220px;
    width: 100%;
}
.v-card-text {
    min-height: auto;
}
</style>
