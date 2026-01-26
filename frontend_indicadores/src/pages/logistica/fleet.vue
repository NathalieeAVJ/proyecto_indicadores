<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Gestión de Flota Vehicular</h1>
        <p class="text-subtitle-1 text-grey">Control operativo de unidades, consumos de combustible y servicios técnicos</p>
      </v-col>
    </v-row>

    <!-- TABS -->
    <v-card variant="outlined" class="rounded-xl overflow-hidden mb-6">
      <v-tabs v-model="tab" color="primary" bg-color="grey-lighten-4">
        <v-tab value="units" prepend-icon="mdi-car-multiple">Unidades (Vehículos)</v-tab>
        <v-tab value="fuel" prepend-icon="mdi-gas-station">Consumo de Combustible</v-tab>
        <v-tab value="maintenance" prepend-icon="mdi-wrench-clock">Mantenimiento Vehicular</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <!-- UNITS TAB -->
        <v-window-item value="units">
          <v-card-text class="pa-4">
            <v-row class="mb-4 align-center">
              <v-col cols="12" md="8">
                <v-text-field v-model="searchUnits" prepend-inner-icon="mdi-magnify" label="Buscar por placa, marca o modelo..." variant="outlined" density="compact" hide-details></v-text-field>
              </v-col>
              <v-col cols="12" md="4" class="text-right">
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openUnitDialog">Registrar Vehículo</v-btn>
              </v-col>
            </v-row>
            <v-data-table :headers="unitHeaders" :items="vehicles" :search="searchUnits" :loading="loading" class="elevation-0">
              <template v-slot:item.plate="{ item }">
                <v-chip color="secondary" variant="flat" size="small" class="font-weight-bold">{{ item.plate }}</v-chip>
              </template>
              <template v-slot:item.status="{ item }">
                <v-chip :color="getVehicleStatusColor(item.status)" size="x-small" label class="text-uppercase">{{ item.status_display }}</v-chip>
              </template>
              <template v-slot:item.odometer="{ item }">
                <span class="font-weight-bold">{{ Number(item.odometer).toLocaleString() }} Km</span>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-pencil" size="x-small" variant="text" color="info" @click="editUnit(item)"></v-btn>
                <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click="deleteUnit(item.id)"></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>

        <!-- FUEL TAB -->
        <v-window-item value="fuel">
          <v-card-text class="pa-4">
             <v-row class="mb-4 align-center">
              <v-col cols="12" md="8">
                <v-text-field v-model="searchFuel" prepend-inner-icon="mdi-magnify" label="Buscar por placa o estación..." variant="outlined" density="compact" hide-details></v-text-field>
              </v-col>
              <v-col cols="12" md="4" class="text-right">
                <v-btn color="secondary" prepend-icon="mdi-gas-station" @click="openFuelDialog">Registrar Carga</v-btn>
              </v-col>
            </v-row>
            <v-data-table :headers="fuelHeaders" :items="fuelLogs" :search="searchFuel" :loading="loading" class="elevation-0">
                <template v-slot:item.cost_total="{ item }">
                    <span class="text-success font-weight-bold">${{ item.cost_total }}</span>
                </template>
                 <template v-slot:item.liters="{ item }">
                    {{ item.liters }} L
                </template>
                <template v-slot:item.date="{ item }">
                    {{ item.date }}
                </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>

        <!-- MAINTENANCE TAB -->
        <v-window-item value="maintenance">
          <v-card-text class="pa-4">
            <v-row class="mb-4 align-center">
              <v-col cols="12" md="8">
                <v-text-field v-model="searchMaint" prepend-inner-icon="mdi-magnify" label="Buscar reparaciones..." variant="outlined" density="compact" hide-details></v-text-field>
              </v-col>
              <v-col cols="12" md="4" class="text-right">
                <v-btn color="info" prepend-icon="mdi-tools" @click="openMaintDialog">Reportar Mantenimiento</v-btn>
              </v-col>
            </v-row>
            <v-data-table :headers="maintHeaders" :items="maintenances" :search="searchMaint" :loading="loading" class="elevation-0">
                <template v-slot:item.type="{ item }">
                    <v-chip size="x-small" :color="getMaintTypeColor(item.type)" variant="outlined">{{ item.type_display }}</v-chip>
                </template>
                <template v-slot:item.cost="{ item }">
                    <span class="font-weight-bold">${{ item.cost }}</span>
                </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>
      </v-window>
    </v-card>

    <!-- VEHICLE DIALOG -->
    <v-dialog v-model="unitDialog" max-width="600">
      <v-card :title="isEditUnit ? 'Editar Unidad' : 'Registrar Nuevo Vehículo'" class="rounded-xl">
        <v-card-text>
          <v-form ref="unitFormRef">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="formUnit.plate" label="Placa" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select v-model="formUnit.status" :items="statusOptions" label="Estado Operativo" variant="outlined"></v-select>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="formUnit.brand" label="Marca" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="formUnit.model" label="Modelo" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="formUnit.year" label="Año" type="number" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formUnit.odometer" label="Odómetro Inicial (Km)" type="number" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formUnit.color" label="Color" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                 <v-text-field v-model="formUnit.insurance_policy" label="Póliza de Seguro" variant="outlined"></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                 <v-text-field v-model="formUnit.insurance_expiry" label="Vencimiento Seguro" type="date" variant="outlined"></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="unitDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="elevated" @click="saveUnit" :loading="saving">Guardar Unidad</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- FUEL DIALOG -->
    <v-dialog v-model="fuelDialog" max-width="500">
        <v-card title="Registrar Consumo de Combustible" class="rounded-xl">
            <v-card-text>
                <v-form ref="fuelFormRef">
                    <v-row>
                        <v-col cols="12">
                            <v-autocomplete v-model="formFuel.vehicle" :items="vehicles" item-title="plate" item-value="id" label="Vehículo" variant="outlined" required></v-autocomplete>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="formFuel.date" label="Fecha" type="date" variant="outlined"></v-text-field>
                        </v-col>
                         <v-col cols="12" md="6">
                            <v-text-field v-model="formFuel.odometer_reading" label="Odómetro Actual (Km)" type="number" variant="outlined" required></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="formFuel.liters" label="Litros" type="number" step="0.01" variant="outlined" required></v-text-field>
                        </v-col>
                         <v-col cols="12" md="6">
                            <v-text-field v-model="formFuel.cost_total" label="Costo Total ($)" prefix="$" type="number" step="0.01" variant="outlined" required></v-text-field>
                        </v-col>
                        <v-col cols="12">
                            <v-text-field v-model="formFuel.station" label="Estación de Servicio" variant="outlined" placeholder="Ej: PDV Las Mercedes"></v-text-field>
                        </v-col>
                        <v-col cols="12">
                            <v-text-field v-model="formFuel.driver_name" label="Conductor / Responsable" variant="outlined"></v-text-field>
                        </v-col>
                    </v-row>
                </v-form>
            </v-card-text>
            <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="fuelDialog = false">Cancelar</v-btn>
                <v-btn color="secondary" variant="elevated" @click="saveFuel" :loading="saving">Registrar Carga</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- MAINTENANCE DIALOG -->
    <v-dialog v-model="maintDialog" max-width="600">
        <v-card title="Reportar Mantenimiento / Reparación" class="rounded-xl">
            <v-card-text>
                <v-form ref="maintFormRef">
                    <v-row>
                        <v-col cols="12">
                            <v-autocomplete v-model="formMaint.vehicle" :items="vehicles" item-title="plate" item-value="id" label="Vehículo" variant="outlined" required></v-autocomplete>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="formMaint.date" label="Fecha del Servicio" type="date" variant="outlined"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-select v-model="formMaint.type" :items="maintTypeOptions" label="Tipo" variant="outlined"></v-select>
                        </v-col>
                        <v-col cols="12">
                            <v-textarea v-model="formMaint.description" label="Descripción del Trabajo" variant="outlined" rows="3" required></v-textarea>
                        </v-col>
                        <v-col cols="12" md="6">
                             <v-text-field v-model="formMaint.performed_by" label="Taller / Responsable" variant="outlined" required></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="formMaint.cost" label="Costo ($)" prefix="$" type="number" variant="outlined"></v-text-field>
                        </v-col>
                    </v-row>
                </v-form>
            </v-card-text>
             <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="maintDialog = false">Cancelar</v-btn>
                <v-btn color="info" variant="elevated" @click="saveMaint" :loading="saving">Guardar Servicio</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const tab = ref('units');
const loading = ref(false);
const saving = ref(false);

const vehicles = ref([]);
const fuelLogs = ref([]);
const maintenances = ref([]);

const searchUnits = ref('');
const searchFuel = ref('');
const searchMaint = ref('');

// DIALOGS
const unitDialog = ref(false);
const isEditUnit = ref(false);
const fuelDialog = ref(false);
const maintDialog = ref(false);

// FORMS
const formUnit = ref({ plate: '', brand: '', model: '', year: 2024, odometer: 0, status: 'operative', color: '', insurance_policy: '', insurance_expiry: '' });
const formFuel = ref({ vehicle: null, date: new Date().toISOString().substr(0, 10), liters: 0, cost_total: 0, odometer_reading: 0, station: '', driver_name: '' });
const formMaint = ref({ vehicle: null, date: new Date().toISOString().substr(0, 10), type: 'preventive', description: '', cost: 0, performed_by: '' });

const unitHeaders = [
    { title: 'Placa', key: 'plate' },
    { title: 'Vehículo', value: i => `${i.brand} ${i.model}` },
    { title: 'Kilometraje', key: 'odometer', align: 'end' },
    { title: 'Estado', key: 'status', align: 'center' },
    { title: 'Acciones', key: 'actions', sortable: false, align: 'end' }
];

const fuelHeaders = [
    { title: 'Fecha', key: 'date' },
    { title: 'Vehículo', key: 'vehicle_plate' },
    { title: 'Litros', key: 'liters', align: 'end' },
    { title: 'Costo', key: 'cost_total', align: 'end' },
    { title: 'Odómetro', key: 'odometer_reading', align: 'end' },
    { title: 'Conductor', key: 'driver_name' }
];

const maintHeaders = [
    { title: 'Fecha', key: 'date' },
    { title: 'Vehículo', key: 'vehicle_plate' },
    { title: 'Tipo', key: 'type', align: 'center' },
    { title: 'Descripción', key: 'description' },
    { title: 'Costo', key: 'cost', align: 'end' }
];

const statusOptions = [
    { title: 'Operativo', value: 'operative' },
    { title: 'En Taller', value: 'maintenance' },
    { title: 'Fuera de Servicio', value: 'broken' },
    { title: 'Alquilado', value: 'leased' }
];

const maintTypeOptions = [
    { title: 'Preventivo', value: 'preventive' },
    { title: 'Correctivo', value: 'corrective' },
    { title: 'Inspección', value: 'inspection' }
];

const loadData = async () => {
    loading.value = true;
    try {
        const [vRes, fRes, mRes] = await Promise.all([
            api.get('logistica/vehicles/'),
            api.get('logistica/fuel-logs/'),
            api.get('logistica/maintenances/')
        ]);
        vehicles.value = vRes;
        fuelLogs.value = fRes;
        maintenances.value = mRes;
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

const openUnitDialog = () => {
    isEditUnit.value = false;
    formUnit.value = { plate: '', brand: '', model: '', year: 2024, odometer: 0, status: 'operative', color: '', insurance_policy: '', insurance_expiry: '' };
    unitDialog.value = true;
};

const editUnit = (item) => {
    isEditUnit.value = true;
    formUnit.value = { ...item };
    unitDialog.value = true;
};

const saveUnit = async () => {
    saving.value = true;
    try {
        if (isEditUnit.value) {
            await api.patch(`logistica/vehicles/${formUnit.value.id}/`, formUnit.value);
        } else {
            await api.post('logistica/vehicles/', formUnit.value);
        }
        unitDialog.value = false;
        loadData();
    } catch (e) { alert('Error al guardar vehículo'); }
    finally { saving.value = false; }
};

const openFuelDialog = () => {
    formFuel.value = { vehicle: null, date: new Date().toISOString().substr(0, 10), liters: 0, cost_total: 0, odometer_reading: 0, station: '', driver_name: '' };
    fuelDialog.value = true;
};

const saveFuel = async () => {
    saving.value = true;
    try {
        await api.post('logistica/fuel-logs/', formFuel.value);
        fuelDialog.value = false;
        loadData();
    } catch (e) { alert('Error al registrar combustible'); }
    finally { saving.value = false; }
};

const openMaintDialog = () => {
    formMaint.value = { vehicle: null, date: new Date().toISOString().substr(0, 10), type: 'preventive', description: '', cost: 0, performed_by: '' };
    maintDialog.value = true;
};

const saveMaint = async () => {
    saving.value = true;
    try {
        await api.post('logistica/maintenances/', formMaint.value);
        maintDialog.value = false;
        loadData();
    } catch (e) { alert('Error al registrar mantenimiento'); }
    finally { saving.value = false; }
};

const getVehicleStatusColor = (s) => ({
    operative: 'success',
    maintenance: 'warning',
    broken: 'error',
    leased: 'info'
}[s] || 'grey');

const getMaintTypeColor = (t) => ({
    preventive: 'info',
    corrective: 'error',
    inspection: 'success'
}[t] || 'grey');

onMounted(loadData);
</script>
