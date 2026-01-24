<template>
  <v-container>
    <v-row v-if="loading">
        <v-col class="text-center"><v-progress-circular indeterminate color="primary"></v-progress-circular></v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12">
        <v-card class="mb-6 elevation-2 rounded-lg py-4 px-6 bg-surface">
            <div class="d-flex align-center">
                <v-avatar color="primary" size="64" class="mr-4">
                    <span class="text-h4 text-white">{{ employee.first_name[0] }}{{ employee.last_name[0] }}</span>
                </v-avatar>
                <div>
                    <h1 class="text-h4 font-weight-bold">{{ employee.first_name }} {{ employee.last_name }}</h1>
                    <p class="text-subtitle-1 text-grey-darken-1">{{ employee.position }} | {{ employee.department }}</p>
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
            <v-tab value="payroll" prepend-icon="mdi-cash">Pagos</v-tab>
          </v-tabs>

          <v-window v-model="tab">
            <!-- GENERAL TAB -->
            <v-window-item value="general">
              <v-card-text class="pa-6">
                <v-form @submit.prevent="updateGeneral">
                  <v-row>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.dni" label="Cédula/ID" readonly variant="filled"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.email" label="Correo" type="email"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.phone" label="Teléfono"></v-text-field></v-col>
                    <v-col cols="12" md="4">
                        <v-select v-model="employee.contract_type" :items="contractTypes" item-title="title" item-value="value" label="Tipo de Contrato"></v-select>
                    </v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.base_salary" label="Sueldo Base" prefix="$"></v-text-field></v-col>
                    <v-col cols="12" md="4"><v-text-field v-model="employee.hcm_policy_number" label="Póliza HCM"></v-text-field></v-col>
                    <v-col cols="12"><v-textarea v-model="employee.address" label="Dirección Habitual" rows="2"></v-textarea></v-col>
                    <v-col cols="12"><v-text-field v-model="employee.emergency_contact" label="Contacto de Emergencia (Nombre y Telefono)"></v-text-field></v-col>
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
                <div class="d-flex justify-space-between mb-4">
                    <h3>Cargas Familiares</h3>
                    <v-btn size="small" color="secondary" prepend-icon="mdi-plus" @click="showFamilyDialog = true">Agregar Pariente</v-btn>
                </div>
                <v-table density="compact">
                    <thead><tr><th>Nombre</th><th>Parentesco</th><th>Fecha Nac.</th><th>DNI</th><th>Acciones</th></tr></thead>
                    <tbody>
                        <tr v-for="member in employee.family" :key="member.id">
                            <td>{{ member.full_name }}</td>
                            <td>{{ member.relationship }}</td>
                            <td>{{ formatDate(member.birth_date) }}</td>
                            <td>{{ member.dni }}</td>
                            <td><v-btn icon="mdi-delete" size="x-small" color="error" variant="text" @click="removeFamily(member.id)"></v-btn></td>
                        </tr>
                    </tbody>
                </v-table>
              </v-card-text>
            </v-window-item>

            <!-- EQUIPMENT TAB -->
            <v-window-item value="equipment">
              <v-card-text class="pa-6">
                <div class="d-flex justify-space-between mb-4">
                    <h3>Activos Asignados</h3>
                    <v-btn size="small" color="secondary" prepend-icon="mdi-plus" @click="showEquipDialog = true">Asignar Equipo</v-btn>
                </div>
                <v-row>
                    <v-col v-for="item in employee.equipment" :key="item.id" cols="12" md="4">
                        <v-card border flat class="rounded-lg position-relative">
                            <v-btn icon="mdi-close" size="x-small" color="error" class="position-absolute" style="top: 5px; right: 5px;" variant="text" @click="returnEquip(item.id)"></v-btn>
                            <v-card-text class="d-flex align-center">
                                <v-icon size="large" color="primary" class="mr-3">{{ getEquipmentIcon(item.category) }}</v-icon>
                                <div>
                                    <div class="font-weight-bold">{{ item.item_name }}</div>
                                    <div class="text-caption">S/N: {{ item.serial_number }}</div>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
              </v-card-text>
            </v-window-item>

            <!-- ABSENCES TAB -->
            <v-window-item value="absences">
                <v-card-text class="pa-6">
                    <div class="d-flex justify-space-between mb-4">
                        <h3>Vacaciones y Permisos</h3>
                        <v-btn size="small" color="secondary" prepend-icon="mdi-calendar-plus" @click="showAbsenceDialog = true">Solicitar Permiso</v-btn>
                    </div>
                    <v-list lines="two">
                        <v-list-item v-for="abs in employee.absences" :key="abs.id" :title="abs.type.toUpperCase()" :subtitle="abs.reason">
                            <template v-slot:prepend>
                                <v-icon :color="getAbsenceColor(abs.status)">mdi-calendar-check</v-icon>
                            </template>
                            <template v-slot:append>
                                <div class="text-right">
                                    <div class="text-caption font-weight-bold">{{ formatDate(abs.start_date) }} - {{ formatDate(abs.end_date) }}</div>
                                    <v-chip size="x-small" :color="getAbsenceColor(abs.status)">{{ getAbsenceLabel(abs.status) }}</v-chip>
                                </div>
                            </template>
                        </v-list-item>
                    </v-list>
                </v-card-text>
            </v-window-item>
...
    <!-- MODALS -->
    <v-dialog v-model="showFamilyDialog" max-width="500px">
        <v-card title="Nuevo Familiar">
            <v-card-text>
                <v-text-field v-model="familyForm.full_name" label="Nombre Completo"></v-text-field>
                <v-select v-model="familyForm.relationship" :items="relationships" item-title="title" item-value="value" label="Parentesco"></v-select>
                <v-text-field v-model="familyForm.dni" label="DNI"></v-text-field>
                <v-text-field v-model="familyForm.birth_date" label="Fecha Nac." type="date"></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn @click="showFamilyDialog = false">Cancelar</v-btn>
                <v-btn color="primary" @click="addFamily">Guardar</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-dialog v-model="showAbsenceDialog" max-width="500px">
        <v-card title="Nueva Solicitud">
            <v-card-text>
                <v-select v-model="absenceForm.type" :items="absenceTypes" item-title="title" item-value="value" label="Tipo"></v-select>
                <v-textarea v-model="absenceForm.reason" label="Motivo"></v-textarea>
                <v-row>
                    <v-col><v-text-field v-model="absenceForm.start_date" label="Inicio" type="date"></v-text-field></v-col>
                    <v-col><v-text-field v-model="absenceForm.end_date" label="Fin" type="date"></v-text-field></v-col>
                </v-row>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn @click="showAbsenceDialog = false">Cancelar</v-btn>
                <v-btn color="primary" @click="addAbsence">Enviar Solicitud</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-dialog v-model="showEquipDialog" max-width="500px">
        <v-card title="Asignar Equipo">
            <v-card-text>
                <v-text-field v-model="equipForm.item_name" label="Equipo"></v-text-field>
                <v-select v-model="equipForm.category" :items="equipCategories" item-title="title" item-value="value" label="Categoría"></v-select>
                <v-text-field v-model="equipForm.serial_number" label="S/N"></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn @click="showEquipDialog = false">Cancelar</v-btn>
                <v-btn color="primary" @click="addEquip">Asignar</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>


            <!-- PAYROLL TAB -->
            <v-window-item value="payroll">
                <v-card-text class="pa-6">
                    <h3 class="mb-4">Histórico de Pagos</h3>
                    <v-table density="compact">
                        <thead><tr><th>Mes/Año</th><th>Sueldo</th><th>Bonos</th><th>Deducciones</th><th>Neto</th><th>Acciones</th></tr></thead>
                        <tbody>
                            <tr v-for="pay in payrolls" :key="pay.id">
                                <td>{{ pay.period_month }}/{{ pay.period_year }}</td>
                                <td>${{ pay.base_salary }}</td>
                                <td class="text-success">+ ${{ pay.bonuses }}</td>
                                <td class="text-error">- ${{ pay.deductions }}</td>
                                <td class="font-weight-bold">${{ pay.net_salary }}</td>
                                <td>
                                    <v-btn icon="mdi-file-pdf-box" size="x-small" color="primary" variant="text" @click="downloadReceipt(pay)"></v-btn>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-card-text>
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import { formatDate } from '@/utils/format';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const downloadReceipt = (pay) => {
    const doc = new jsPDF();
    
    // Header
    doc.setFontSize(22);
    doc.setTextColor(149, 117, 205); // Primary Purple
    doc.text('NatTelf', 20, 20);
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text('Recibo de Pago de Nómina', 20, 28);
    
    // Employee Info
    doc.setFontSize(12);
    doc.setTextColor(0);
    doc.text(`Empleado: ${employee.value.first_name} ${employee.value.last_name}`, 20, 45);
    doc.text(`Cédula/DNI: ${employee.value.dni}`, 20, 52);
    doc.text(`Cargo: ${employee.value.position}`, 20, 59);
    doc.text(`Periodo: ${pay.period_month}/${pay.period_year}`, 140, 45);
    doc.text(`Fecha Emisión: ${formatDate(new Date())}`, 140, 52);
    
    // Table
    autoTable(doc, {
        startY: 70,
        head: [['Descripción', 'Monto']],
        body: [
            ['Sueldo Base', `$${pay.base_salary}`],
            ['Bonificaciones', `$${pay.bonuses}`],
            ['Deducciones', `-$${pay.deductions}`],
            ['Sueldo Neto', `$${pay.net_salary}`]
        ],
        theme: 'striped',
        headStyles: { fillColor: [149, 117, 205] },
        alternateRowStyles: { fillColor: [243, 229, 245] }
    });
    
    // Footer
    const finalY = doc.lastAutoTable.finalY + 30;
    doc.line(20, finalY, 80, finalY);
    doc.text('Firma del Empleado', 35, finalY + 5);
    
    doc.line(130, finalY, 190, finalY);
    doc.text('Administración NatTelf', 145, finalY + 5);
    
    doc.save(`Recibo_NatTelf_${employee.value.dni}_${pay.period_month}_${pay.period_year}.pdf`);
};

const route = useRoute();
const router = useRouter();
const tab = ref('general');
const employee = ref(null);
const payrolls = ref([]);
const loading = ref(true);
const saving = ref(false);

const contractTypes = [
  { title: 'Fijo / Indeterminado', value: 'permanent' },
  { title: 'Contratado / Determinado', value: 'temporary' },
  { title: 'Pasante', value: 'intern' },
];

const getStatusColor = (s) => {
    if (s === 'active') return 'success';
    if (s === 'vacation') return 'info';
    return 'warning';
};

const getEquipmentIcon = (cat) => {
    if (cat === 'laptop') return 'mdi-laptop';
    if (cat === 'phone') return 'mdi-cellphone';
    if (cat === 'tool') return 'mdi-wrench';
    return 'mdi-card-account-details';
};

const getAbsenceColor = (s) => {
    if (s === 'approved') return 'success';
    if (s === 'pending') return 'warning';
    return 'error';
};

const loadEmployee = async () => {
    loading.value = true;
    try {
        const [emp, pay] = await Promise.all([
            api.get(`employees/${route.params.id}/`),
            api.get(`payroll/?employee=${route.params.id}`)
        ]);
        employee.value = emp;
        payrolls.value = pay;
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

// MODALS & FORMS
const showFamilyDialog = ref(false);
const familyForm = ref({ full_name: '', relationship: '', dni: '', birth_date: '' });
const relationships = [
    { title: 'Esposo/a', value: 'spouse' },
    { title: 'Hijo/a', value: 'child' },
    { title: 'Padre/Madre', value: 'parent' }
];

const showAbsenceDialog = ref(false);
const absenceForm = ref({ type: 'vacation', reason: '', start_date: '', end_date: '' });
const absenceTypes = [
    { title: 'Vacaciones', value: 'vacation' },
    { title: 'Reposo Médico', value: 'medical' },
    { title: 'Permiso Personal', value: 'personal' }
];

const showEquipDialog = ref(false);
const equipForm = ref({ item_name: '', category: 'laptop', serial_number: '' });
const equipCategories = [
    { title: 'PC/Laptop', value: 'laptop' },
    { title: 'Celular', value: 'phone' },
    { title: 'Herramienta', value: 'tool' },
    { title: 'Uniforme', value: 'uniform' }
];

// ACTIONS
const addFamily = async () => {
    try {
        await api.post('family-members/', { ...familyForm.value, employee: employee.value.id });
        showFamilyDialog.value = false;
        loadEmployee();
    } catch (e) { alert('Error al guardar familiar'); }
};

const removeFamily = async (id) => {
    if (confirm('¿Eliminar este pariente?')) {
        await api.delete(`family-members/${id}/`);
        loadEmployee();
    }
};

const addAbsence = async () => {
    try {
        await api.post('absences/', { ...absenceForm.value, employee: employee.value.id });
        showAbsenceDialog.value = false;
        loadEmployee();
    } catch (e) { alert('Error en la solicitud'); }
};

const addEquip = async () => {
    try {
        await api.post('equipment/', { ...equipForm.value, employee: employee.value.id });
        showEquipDialog.value = false;
        loadEmployee();
    } catch (e) { alert('Error al asignar'); }
};

const returnEquip = async (id) => {
    if (confirm('¿Marcar como devuelto/retirado?')) {
        await api.delete(`equipment/${id}/`);
        loadEmployee();
    }
};

const updateGeneral = async () => {
    saving.value = true;
    try {
        await api.patch(`employees/${route.params.id}/`, employee.value);
        alert('Datos actualizados');
    } catch (e) {
        console.error(e);
    } finally {
        saving.value = false;
    }
};

onMounted(loadEmployee);
</script>
