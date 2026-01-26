<template>
  <v-container>
    <v-row v-if="loading">
      <v-col class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12">
        <!-- HEADER CARD -->
        <v-card class="mb-6 elevation-2 rounded-lg py-4 px-6 bg-surface">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="64" class="mr-4">
              <span class="text-h4 text-white">{{ employee.first_name[0] }}{{ employee.last_name[0] }}</span>
            </v-avatar>
            <div>
              <h1 class="text-h4 font-weight-bold">{{ employee.first_name }} {{ employee.last_name }}</h1>
              <p class="text-subtitle-1 text-grey-darken-1">
                {{ employee.position }} | {{ employee.department_detail?.name || employee.department || 'Sin Dept.' }}
              </p>
            </div>
            <v-spacer></v-spacer>
            <v-chip :color="getStatusColor(employee.status)" class="text-uppercase font-weight-bold">
              {{ employee.status }}
            </v-chip>
          </div>
        </v-card>

        <v-card elevation="2" class="rounded-lg">
          <v-tabs v-model="tab" color="primary" align-tabs="start">
            <v-tab value="general" prepend-icon="mdi-account">General</v-tab>
            <v-tab value="family" prepend-icon="mdi-account-group">Familia</v-tab>
            <v-tab value="equipment" prepend-icon="mdi-tools">Equipos</v-tab>
            <v-tab value="absences" prepend-icon="mdi-calendar-clock">Ausencias</v-tab>
            <v-tab value="performance" prepend-icon="mdi-trending-up">Desempeño</v-tab>
            <v-tab value="payroll" prepend-icon="mdi-cash">Pagos</v-tab>
            <v-tab value="audit" v-if="authStore.isAdmin" prepend-icon="mdi-shield-check">Auditoría</v-tab>
          </v-tabs>

          <v-window v-model="tab">
            <!-- GENERAL TAB -->
            <v-window-item value="general">
              <v-card-text class="pa-6">
                <v-form @submit.prevent="updateGeneral" id="generalForm">
                  <v-row>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.dni" label="Cédula" readonly variant="filled"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.email" label="Correo" type="email"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.phone" label="Teléfono"></v-text-field></v-col>
                    <v-col cols="12" md="4">
                      <v-select v-model="employee.contract_type" :items="contractTypes" label="Tipo de Contrato"></v-select>
                    </v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.base_salary" label="Sueldo Base" prefix="$" type="number"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.hcm_policy_number" label="Póliza HCM"></v-text-field></v-col>
                    <v-col cols="12"><v-textarea v-model="employee.address" label="Dirección Habitual" rows="2"></v-textarea></v-col>
                    <v-col cols="12"><v-text-field v-model="employee.emergency_contact" label="Contacto de Emergencia"></v-text-field></v-col>
                  </v-row>
                  <div class="d-flex justify-end mt-4">
                    <v-btn color="primary" type="submit" :loading="saving">Actualizar Datos</v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-window-item>

            <!-- FAMILY TAB -->
            <v-window-item value="family">
              <v-card-text class="pa-6">
                <div class="d-flex justify-space-between mb-4 align-center">
                  <h3>Cargas Familiares</h3>
                  <v-btn size="small" color="secondary" prepend-icon="mdi-plus" @click="showFamilyDialog = true">Agregar</v-btn>
                </div>
                <v-data-table :headers="familyHeaders" :items="employee.family" density="compact">
                  <template v-slot:item.relationship="{ item }">
                    {{ getRelationshipLabel(item.relationship) }}
                  </template>
                  <template v-slot:item.birth_date="{ item }">{{ formatDate(item.birth_date) }}</template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn icon="mdi-pencil" size="x-small" color="primary" variant="text" @click="openEditFamily(item)"></v-btn>
                    <v-btn icon="mdi-delete" size="x-small" color="error" variant="text" @click="removeFamily(item.id)"></v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-window-item>

            <v-window-item value="equipment">
              <v-card-text class="pa-6">
                <div class="d-flex justify-space-between mb-4">
                  <h3>Activos y Herramientas Asignadas</h3>
                  <v-btn v-if="authStore.isAdmin" size="small" color="secondary" prepend-icon="mdi-plus" @click="showEquipDialog = true">Asignar Equipo</v-btn>
                </div>
                <v-row>
                  <v-col v-for="item in employee.equipment" :key="item.id" cols="12" md="6" lg="4">
                    <v-card border flat class="rounded-lg overflow-hidden">
                      <v-card-text class="pa-4">
                        <div class="d-flex align-start">
                          <v-avatar color="primary" variant="tonal" rounded="lg" class="mr-3">
                            <v-icon>{{ getEquipmentIcon(item.category) }}</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <div class="d-flex justify-space-between align-center mb-1">
                              <span class="text-caption font-weight-bold grey--text">{{ item.internal_code || 'S/C' }}</span>
                              <v-chip size="x-small" :color="getEquipStatusColor(item.status)" class="text-uppercase font-weight-bold">
                                {{ getEquipStatusLabel(item.status) }}
                              </v-chip>
                            </div>
                            <div class="text-h6 font-weight-bold leading-tight mb-1">{{ item.item_name }}</div>
                            <div class="text-caption text-grey-darken-1">{{ item.brand }} {{ item.model }}</div>
                            <div class="text-caption mt-1">S/N: {{ item.serial_number }}</div>
                          </div>
                        </div>
                        
                        <v-divider class="my-3"></v-divider>
                        
                        <div class="d-flex justify-space-between">
                          <v-btn 
                            v-if="item.status === 'functional' || item.status === 'failing'"
                            size="x-small" 
                            color="error" 
                            variant="tonal" 
                            prepend-icon="mdi-alert-circle-outline" 
                            @click="openFaultDialog(item)"
                          >
                            Reportar Falla
                          </v-btn>
                          <v-spacer></v-spacer>
                          <v-btn v-if="authStore.isAdmin" icon="mdi-close" size="x-small" color="grey" variant="text" @click="returnEquip(item.id)"></v-btn>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                <v-alert v-if="!employee.equipment?.length" type="info" variant="tonal" class="mt-4">
                  No tienes equipos asignados actualmente.
                </v-alert>
              </v-card-text>
            </v-window-item>

            <!-- ABSENCES TAB -->
            <v-window-item value="absences">
              <v-card-text class="pa-6">
                <div class="d-flex justify-space-between mb-4">
                  <h3>Historial de Ausencias</h3>
                  <v-btn size="small" color="secondary" prepend-icon="mdi-calendar-plus" @click="showAbsenceDialog = true">Solicitar</v-btn>
                </div>
                <v-data-table :items="employee.absences" :headers="[{title:'Tipo', key:'type'}, {title:'Fecha', key:'date'}, {title:'Estado', key:'status'}]">
                   <template v-slot:item.date="{ item }">{{ formatDate(item.start_date) }} - {{ formatDate(item.end_date) }}</template>
                   <template v-slot:item.status="{ item }">
                     <v-chip size="x-small" :color="getAbsenceColor(item.status)">{{ getAbsenceLabel(item.status) || item.status }}</v-chip>
                   </template>
                </v-data-table>
              </v-card-text>
            </v-window-item>

            <!-- PERFORMANCE TAB -->
            <v-window-item value="performance">
              <v-card-text class="pa-6">
                <div class="d-flex justify-space-between mb-4 align-center">
                  <div>
                    <h3 class="mb-1">Evaluación de Desempeño Mensual</h3>
                    <p class="text-caption text-grey">Historial de calificaciones y feedback corporativo</p>
                  </div>
                  <v-btn color="primary" prepend-icon="mdi-star-plus" @click="showEvalDialog = true">Evaluar Mes</v-btn>
                </div>

                <!-- NEW: TREND CHART -->
                <v-card variant="outlined" class="mb-6 rounded-lg pa-4" v-if="evaluations.length > 0">
                    <div style="height: 250px;">
                        <Line :data="performanceChartConfig.data" :options="performanceChartConfig.options" />
                    </div>
                </v-card>

                <v-data-table :headers="performanceHeaders" :items="evaluations" :loading="loadingEval" class="border rounded-lg">
                  <template v-slot:item.period="{ item }">{{ months[item.period_month - 1] }} {{ item.period_year }}</template>
                  <template v-slot:item.score="{ item }">
                    <v-chip :color="getScoreColor(item.score)" size="small" class="font-weight-bold">{{ item.score }} / 100</v-chip>
                  </template>
                  <template v-slot:item.bonus="{ item }">
                    <div class="d-flex align-center justify-center">
                        <v-chip v-if="item.suggested_bonus > 0" :color="item.bonus_approved ? 'success' : 'warning'" size="x-small" label>
                            <v-icon start size="x-small">mdi-cash-plus</v-icon>
                            ${{ item.suggested_bonus }}
                        </v-chip>
                        <v-btn 
                            v-if="item.suggested_bonus > 0 && !item.bonus_approved && authStore.isAdmin" 
                            icon="mdi-check" 
                            size="x-small" 
                            color="success" 
                            variant="text" 
                            class="ml-1"
                            title="Aprobar Bono"
                            @click="approveBonus(item.id)"
                        ></v-btn>
                        <span v-else-if="item.suggested_bonus <= 0" class="text-caption text-grey">N/A</span>
                    </div>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-window-item>

            <!-- PAYROLL TAB -->
            <v-window-item value="payroll">
              <v-card-text class="pa-6">
                <h3>Histórico de Pagos</h3>
                <v-data-table :headers="payrollTableHeaders" :items="payrolls">
                  <template v-slot:item.period="{ item }">{{ item.period_month }}/{{ item.period_year }}</template>
                  <template v-slot:item.net_salary="{ item }">${{ item.net_salary }}</template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn icon="mdi-file-pdf-box" size="small" color="primary" variant="text" @click="downloadReceipt(item)"></v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-window-item>

            <!-- AUDIT TAB -->
            <v-window-item value="audit" v-if="authStore.isAdmin">
              <v-card-text class="pa-6">
                <v-data-table :headers="auditHeaders" :items="auditLogs" :loading="loadingAudit">
                  <template v-slot:item.action="{ item }">
                    <v-chip size="x-small" :color="getActionColor(item.action)">{{ item.action.toUpperCase() }}</v-chip>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>
    </v-row>

    <!-- MODALS -->
    <v-dialog v-model="showFamilyDialog" max-width="500px">
      <v-card :title="isEditingFamily ? 'Editar Familiar' : 'Agregar Familiar'">
        <v-card-text>
          <v-text-field v-model="familyForm.full_name" label="Nombre"></v-text-field>
          <v-select v-model="familyForm.relationship" :items="relationships" label="Parentesco"></v-select>
          <v-text-field v-model="familyForm.dni" label="Cédula"></v-text-field>
          <v-text-field v-model="familyForm.birth_date" label="F. Nac" type="date"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="closeFamilyDialog">Cerrar</v-btn>
          <v-btn color="primary" @click="saveFamily" :loading="savingFamily">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showAbsenceDialog" max-width="500px">
      <v-card title="Solicitud">
        <v-card-text>
          <v-select v-model="absenceForm.type" :items="absenceTypes" label="Tipo"></v-select>
          <v-textarea v-model="absenceForm.reason" label="Motivo"></v-textarea>
          <v-row>
            <v-col><v-text-field v-model="absenceForm.start_date" type="date" label="Inicio"></v-text-field></v-col>
            <v-col><v-text-field v-model="absenceForm.end_date" type="date" label="Fin"></v-text-field></v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showAbsenceDialog = false">Cerrar</v-btn>
          <v-btn color="primary" @click="addAbsence">Enviar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showEquipDialog" max-width="500px">
      <v-card title="Asignar Activo">
        <v-card-text>
          <v-text-field v-model="equipForm.item_name" label="Equipo"></v-text-field>
          <v-select v-model="equipForm.category" :items="equipCategories" label="Categoría"></v-select>
          <v-text-field v-model="equipForm.serial_number" label="S/N"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showEquipDialog = false">Cerrar</v-btn>
          <v-btn color="primary" @click="addEquip">Asignar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showEvalDialog" max-width="600px">
      <v-card title="Evaluar Desempeño">
        <v-card-text>
          <v-row>
            <v-col cols="6"><v-select v-model="evalForm.period_month" :items="monthItems" label="Mes" item-title="title" item-value="value"></v-select></v-col>
            <v-col cols="6"><v-text-field v-model="evalForm.period_year" type="number" label="Año"></v-text-field></v-col>
            <v-col cols="12">
              <label class="text-caption">Calificación: {{ evalForm.score }} / 100</label>
              <v-slider v-model="evalForm.score" color="primary" min="1" max="100"></v-slider>
            </v-col>
            <v-col cols="12">
                <v-textarea v-model="evalForm.comments" label="Feedback / Notas" variant="outlined" rows="2"></v-textarea>
            </v-col>
            <v-col cols="12">
                <v-divider class="mb-4"></v-divider>
                <div class="text-subtitle-2 mb-2">Incentivo por Desempeño</div>
                <v-text-field
                    v-model="evalForm.suggested_bonus"
                    label="Bono Sugerido ($)"
                    prefix="$"
                    type="number"
                    density="compact"
                    variant="filled"
                    hint="Monto que el superior considerará para asignar"
                    persistent-hint
                ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showEvalDialog = false">Cerrar</v-btn>
          <v-btn color="primary" @click="addEvaluation" :loading="savingEval">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- NEW: FAULT REPORT DIALOG -->
    <v-dialog v-model="showFaultDialog" max-width="500px">
      <v-card title="Reportar Falla de Equipo" prepend-icon="mdi-alert-octagon">
        <v-card-text>
          <div v-if="selectedEquip" class="mb-4 pa-3 bg-grey-lighten-4 rounded">
            <div class="text-subtitle-2 font-weight-bold">{{ selectedEquip.item_name }}</div>
            <div class="text-caption">Cód: {{ selectedEquip.internal_code }}</div>
          </div>
          <v-textarea 
            v-model="faultForm.reason" 
            label="Describe el problema o falla" 
            placeholder="Ej: La pantalla no enciende, hace un ruido extraño..."
            rows="4"
            variant="outlined"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showFaultDialog = false">Cancelar</v-btn>
          <v-btn color="error" variant="elevated" @click="submitFault" :loading="savingFault">Enviar Reporte</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { formatDate } from '@/utils/format';
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale);

const authStore = useAuthStore();
const route = useRoute();
const tab = ref('general');
const employee = ref(null);
const payrolls = ref([]);
const evaluations = ref([]);

const performanceChartConfig = computed(() => {
    // Sort evaluations by date ASC for the chart
    const data = [...evaluations.value].sort((a,b) => (a.period_year - b.period_year) || (a.period_month - b.period_month));
    
    return {
        data: {
            labels: data.map(e => `${months[e.period_month - 1]} ${e.period_year}`),
            datasets: [{
                label: 'Tendencia de Desempeño',
                data: data.map(e => e.score),
                borderColor: '#9575CD',
                backgroundColor: '#9575CD',
                tension: 0.3,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0, max: 100, title: { display: true, text: 'Puntaje (%)' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    };
});

const auditLogs = ref([]);
const loading = ref(true);
const loadingEval = ref(false);
const loadingAudit = ref(false);
const saving = ref(false);
const savingEval = ref(false);

const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const monthItems = months.map((m, i) => ({ title: m, value: i + 1 }));

// TABLE HEADERS
const familyHeaders = [{ title: 'Nombre', key: 'full_name' }, { title: 'Parentesco', key: 'relationship' }, { title: 'Cédula', key: 'dni' }, { title: 'Acciones', key: 'actions', align: 'end' }];
const performanceHeaders = [
    { title: 'Periodo', key: 'period' },
    { title: 'Puntaje', key: 'score', align: 'center' },
    { title: 'Bono', key: 'bonus', align: 'center' },
    { title: 'Evaluador', key: 'evaluated_by_name' },
    { title: 'Feedback', key: 'comments' },
];
const payrollTableHeaders = [{ title: 'Periodo', key: 'period' }, { title: 'Neto', key: 'net_salary' }, { title: 'Recibo', key: 'actions', align: 'center' }];
const auditHeaders = [{ title: 'Fecha', key: 'created_at' }, { title: 'Acción', key: 'action' }, { title: 'Descripción', key: 'description' }];

// DATA LOADING
const loadEmployee = async () => {
  loading.value = true;
  try {
    const [emp, pay, evals] = await Promise.all([
      api.get(`employees/${route.params.id}/`),
      api.get(`payroll/?employee=${route.params.id}`),
      api.get(`evaluations/?employee=${route.params.id}`)
    ]);
    employee.value = emp;
    payrolls.value = pay;
    evaluations.value = evals;
    if (authStore.isAdmin) loadAuditLogs();
  } catch (e) { console.error(e); }
  finally { loading.value = false; }
};

const loadAuditLogs = async () => {
  loadingAudit.value = true;
  try { auditLogs.value = await api.get(`audit-logs/?module=employees&object_id=${route.params.id}`); } 
  catch (e) { console.error(e); }
  finally { loadingAudit.value = false; }
};

// FORM DATA
const familyForm = ref({ full_name: '', relationship: 'child', dni: '', birth_date: '' });
const showFamilyDialog = ref(false);
const isEditingFamily = ref(false);
const editingFamilyId = ref(null);
const savingFamily = ref(false);
const relationships = [{title:'Hijo/a', value:'child'}, {title:'Esposo/a', value:'spouse'}, {title:'Padre/Madre', value:'parent'}];

const absenceForm = ref({ type: 'vacation', reason: '', start_date: '', end_date: '' });
const showAbsenceDialog = ref(false);
const absenceTypes = [{title:'Vacaciones', value:'vacation'}, {title:'Médico', value:'medical'}];

const equipForm = ref({ item_name: '', category: 'laptop', serial_number: '', internal_code: '', brand: '', model: '' });
const showEquipDialog = ref(false);
const equipCategories = [
    {title:'Laptop', value:'laptop'}, 
    {title:'Celular', value:'phone'}, 
    {title:'Herramienta', value:'tool'}, 
    {title:'Mueble', value:'furniture'}, 
    {title:'Uniforme', value:'uniform'}, 
    {title:'Carnet', value:'id_card'}
];

const showFaultDialog = ref(false);
const selectedEquip = ref(null);
const faultForm = ref({ reason: '' });
const savingFault = ref(false);

const evalForm = ref({ period_month: new Date().getMonth() + 1, period_year: new Date().getFullYear(), score: 85, comments: '', suggested_bonus: 0 });
const showEvalDialog = ref(false);

// ACTIONS
const openEditFamily = (member) => {
    familyForm.value = { ...member };
    isEditingFamily.value = true;
    editingFamilyId.value = member.id;
    showFamilyDialog.value = true;
};
const closeFamilyDialog = () => {
    showFamilyDialog.value = false;
    isEditingFamily.value = false;
    editingFamilyId.value = null;
    familyForm.value = { full_name: '', relationship: 'child', dni: '', birth_date: '' };
};
const saveFamily = async () => {
    savingFamily.value = true;
    try {
        if (isEditingFamily.value) {
            await api.patch(`family-members/${editingFamilyId.value}/`, { ...familyForm.value, employee: employee.value.id });
        } else {
            await api.post('family-members/', { ...familyForm.value, employee: employee.value.id });
        }
        closeFamilyDialog();
        loadEmployee();
    } catch (e) {
        alert('Error al guardar familiar');
    } finally {
        savingFamily.value = false;
    }
};
const removeFamily = async (id) => { if(confirm('¿Eliminar?')) { await api.delete(`family-members/${id}/`); loadEmployee(); } };
const addAbsence = async () => { await api.post('absences/', { ...absenceForm.value, employee: employee.value.id }); showAbsenceDialog.value = false; loadEmployee(); };
const addEquip = async () => { await api.post('equipment/', { ...equipForm.value, employee: employee.value.id }); showEquipDialog.value = false; loadEmployee(); };
const returnEquip = async (id) => { if(confirm('¿Retirar de cargo?')) { await api.delete(`equipment/${id}/`); loadEmployee(); } };

const openFaultDialog = (item) => {
    selectedEquip.value = item;
    faultForm.value = { reason: '' };
    showFaultDialog.value = true;
};

const submitFault = async () => {
    if (!faultForm.value.reason) return;
    savingFault.value = true;
    try {
        await api.post('hr-requests/', {
            type: 'equip_fault',
            employee: employee.value.id,
            equipment: selectedEquip.value.id,
            reason: faultForm.value.reason
        });
        showFaultDialog.value = false;
        alert('Reporte enviado al departamento técnico.');
        loadEmployee();
    } catch (e) {
        alert('Error al enviar reporte');
    } finally {
        savingFault.value = false;
    }
};

const approveBonus = async (evalId) => {
  if (confirm('¿Desea aprobar este bono por desempeño?')) {
    try {
        await api.post(`evaluations/${evalId}/approve_bonus/`);
        loadEmployee();
    } catch (e) { alert('Error al aprobar bono'); }
  }
};

const addEvaluation = async () => {
  savingEval.value = true;
  try { await api.post('evaluations/', { ...evalForm.value, employee: employee.value.id }); showEvalDialog.value = false; loadEmployee(); }
  catch(e) { alert('Error'); } finally { savingEval.value = false; }
};
const updateGeneral = async () => {
  saving.value = true;
  try { await api.patch(`employees/${route.params.id}/`, employee.value); alert('Actualizado'); }
  finally { saving.value = false; }
};

// HELPERS
const getStatusColor = (s) => s === 'active' ? 'success' : 'warning';
const getRelationshipLabel = (val) => {
  const rel = relationships.find(r => r.value === val);
  return rel ? rel.title : val;
};
const getAbsenceColor = (s) => s === 'approved' ? 'success' : 'warning';
const getAbsenceLabel = (s) => ({pending:'Pendiente', approved:'Aprobado'}[s]);
const getScoreColor = (s) => s >= 80 ? 'success' : (s >= 60 ? 'warning' : 'error');
const getActionColor = (a) => ({create:'success', update:'info'}[a] || 'grey');
const getEquipmentIcon = (cat) => ({
    laptop: 'mdi-laptop',
    phone: 'mdi-cellphone',
    tool: 'mdi-hammer-wrench',
    furniture: 'mdi-seat-recline-normal',
    uniform: 'mdi-tshirt-crew',
    id_card: 'mdi-card-account-details'
}[cat] || 'mdi-package-variant');

const getEquipStatusColor = (s) => ({
    functional: 'success',
    failing: 'warning',
    broken: 'error',
    maintenance: 'info',
    replaced: 'grey'
}[s] || 'grey');

const getEquipStatusLabel = (s) => ({
    functional: 'Operativo',
    failing: 'Falla',
    broken: 'Dañado',
    maintenance: 'En Taller',
    replaced: 'Sustituido'
}[s] || s);

const contractTypes = [{title:'Permanente', value:'permanent'}, {title:'Temporal', value:'temporary'}];

const downloadReceipt = (pay) => {
    const doc = new jsPDF();
    doc.text(`Recibo: ${employee.value.first_name} - Mes ${pay.period_month}`, 20, 20);
    autoTable(doc, { startY: 30, head: [['Detalle', 'Monto']], body: [['Base', `$${pay.base_salary}`], ['Neto', `$${pay.net_salary}`]] });
    doc.save('recibo.pdf');
};

onMounted(loadEmployee);
</script>
