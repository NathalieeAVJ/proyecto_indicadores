<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Editar Incidencia RB #{{ route.params.id }}</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.title" label="Asunto" required></v-text-field>
              
              <v-select
                v-model="form.radio_base"
                :items="radioBases"
                item-title="name"
                item-value="id"
                label="Radiobase Afectada"
                required
              ></v-select>
              
              <v-select
                v-model="form.failure_type"
                :items="failureTypes"
                item-title="name"
                item-value="id"
                label="Tipo de Falla"
                required
              ></v-select>
              
              <v-textarea v-model="form.description" label="Descripción"></v-textarea>
              
              <v-select
                v-model="form.status"
                :items="statuses"
                item-title="title"
                item-value="value"
                label="Estado"
                required
              ></v-select>

              <!-- SECCIÓN DE SOLUCIÓN -->
              <v-expand-transition>
                <div v-if="form.status === 'solved'">
                  <v-divider class="my-4"></v-divider>
                  <h3 class="text-h6 mb-3">Detalles de la Solución</h3>
                  
                  <v-textarea v-model="form.solution_comment" label="Comentarios de Solución"></v-textarea>
                  <v-text-field v-model="form.solved_date" type="datetime-local" label="Fecha Solución"></v-text-field>
                  
                  <!-- REPUESTOS USADOS -->
                  <v-card variant="outlined" class="mt-4">
                    <v-card-title class="text-subtitle-1">
                      <v-icon start>mdi-package-variant</v-icon>
                      Repuestos Utilizados
                    </v-card-title>
                    <v-card-text>
                      <v-row v-for="(item, index) in usedParts" :key="index" class="mb-2">
                        <v-col cols="12" md="6">
                          <v-autocomplete
                            v-model="item.spare_part"
                            :items="spareParts"
                            item-title="name"
                            item-value="id"
                            label="Repuesto"
                            :hint="getStockHint(item.spare_part)"
                            persistent-hint
                          >
                            <template v-slot:item="{ item: spareItem, props }">
                              <v-list-item v-bind="props">
                                <template v-slot:subtitle>
                                  {{ spareItem.raw.code }} - Stock: {{ spareItem.raw.quantity_in_stock }}
                                </template>
                              </v-list-item>
                            </template>
                          </v-autocomplete>
                        </v-col>
                        <v-col cols="12" md="3">
                          <v-text-field
                            v-model.number="item.quantity_used"
                            label="Cantidad"
                            type="number"
                            min="1"
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="3" class="d-flex align-center">
                          <v-btn icon color="error" size="small" @click="removeUsedPart(index)">
                            <v-icon>mdi-delete</v-icon>
                          </v-btn>
                        </v-col>
                      </v-row>
                      
                      <v-btn variant="outlined" size="small" @click="addUsedPart">
                        <v-icon start>mdi-plus</v-icon>
                        Agregar Repuesto
                      </v-btn>
                      
                      <v-alert type="info" variant="tonal" class="mt-3" density="compact" v-if="usedParts.length > 0">
                        Los repuestos seleccionados serán descontados automáticamente del inventario al guardar.
                      </v-alert>
                    </v-card-text>
                  </v-card>
                </div>
              </v-expand-transition>
              
              <v-text-field v-model="form.start_date" type="datetime-local" label="Fecha Inicio" class="mt-4"></v-text-field>
              
              <v-select
                v-model="form.assigned_to"
                :items="users"
                item-title="username"
                item-value="id"
                label="Asignado a"
              ></v-select>

              <v-btn color="primary" type="submit" :loading="loading" class="mt-4">Actualizar</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useRouter, useRoute } from 'vue-router';

const form = ref({});
const radioBases = ref([]);
const failureTypes = ref([]);
const users = ref([]);
const spareParts = ref([]);
const usedParts = ref([]);
const loading = ref(false);
const router = useRouter();
const route = useRoute();
const originalStatus = ref('');

const statuses = [
    { title: 'Pendiente', value: 'pending' },
    { title: 'En Revisión', value: 'in_review' },
    { title: 'Solucionada', value: 'solved' },
    { title: 'Pospuesta', value: 'postponed' },
];

const getStockHint = (partId) => {
  const part = spareParts.value.find(p => p.id === partId);
  return part ? `Disponible: ${part.quantity_in_stock}` : '';
};

const addUsedPart = () => {
  usedParts.value.push({ spare_part: null, quantity_used: 1, notes: '' });
};

const removeUsedPart = (index) => {
  usedParts.value.splice(index, 1);
};

const submit = async () => {
    loading.value = true;
    try {
        // Actualizar la incidencia
        await api.patch(`rb-incidents/${route.params.id}/`, form.value);
        
        // Si se marcó como solucionada y hay repuestos usados, registrarlos
        if (form.value.status === 'solved' && originalStatus.value !== 'solved') {
          for (const item of usedParts.value) {
            if (item.spare_part && item.quantity_used > 0) {
              await api.post('spare-part-usage/', {
                spare_part: item.spare_part,
                quantity_used: item.quantity_used,
                incident_type: 'radiobase',
                incident_id: parseInt(route.params.id),
                notes: item.notes || `Usado en incidencia de radiobase #${route.params.id}`
              });
            }
          }
        }
        
        router.push('/rb-incidents');
    } catch (e) {
        console.error(e);
        const errorMsg = e.data?.quantity_used || e.data?.error || e.message || 'Error al actualizar';
        alert(errorMsg);
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
    try {
        const [incRes, rbRes, typesRes, usersRes, partsRes] = await Promise.all([
             api.get(`rb-incidents/${route.params.id}/`),
             api.get('radio-bases/'),
             api.get('failure-types/'),
             api.get('users/'),
             api.get('spare-parts/')
        ]);
        
        form.value = incRes;
        originalStatus.value = incRes.status;
        
        if(form.value.start_date) form.value.start_date = form.value.start_date.slice(0, 16);
        if(form.value.solved_date) form.value.solved_date = form.value.solved_date.slice(0, 16);
        
        radioBases.value = rbRes;
        failureTypes.value = typesRes;
        users.value = usersRes;
        spareParts.value = partsRes;
    } catch (e) {
        console.error(e);
    }
});
</script>
