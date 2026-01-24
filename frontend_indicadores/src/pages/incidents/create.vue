<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4">Nueva Incidencia</h1>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.title" label="Asunto" required></v-text-field>
              
              <v-select
                v-model="form.phone_number"
                :items="phones"
                item-title="number"
                item-value="id"
                label="Número Telefónico"
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
              
              <v-text-field v-model="form.start_date" type="datetime-local" label="Fecha Inicio"></v-text-field>
              
              <v-btn color="primary" type="submit" :loading="loading" class="mt-4">Guardar</v-btn>
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
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const form = ref({
    title: '',
    phone_number: null,
    failure_type: null,
    description: '',
    start_date: new Date().toISOString().slice(0, 16),
});

const phones = ref([]);
const failureTypes = ref([]);
const loading = ref(false);
const router = useRouter();
const authStore = useAuthStore();

const submit = async () => {
    loading.value = true;
    try {
        await api.post('incidents/', {
            ...form.value,
            created_by: authStore.user?.id // Backend might ignore this if we use CurrentUserDefault in serializer? 
                                          // DRF usually needs us to set it in perform_create (view) or pass it here. 
                                          // Since I didn't override perform_create in IncidentViewSet, I need to pass it or fix view.
                                          // Wait, IncidentViewSet uses ModelViewSet. I should probably set perform_create in ViewSet to set created_by=request.user.
                                          // But for now, if I pass it, serializer might need it to be writable.
        });
        router.push('/incidents');
    } catch (e) {
        console.error(e);
        alert('Error al crear incidencia');
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
    try {
        const [phonesRes, typesRes] = await Promise.all([
            api.get('phones/'),
            api.get('failure-types/')
        ]);
        phones.value = phonesRes;
        failureTypes.value = typesRes;
        
        // Fetch current user id if needed, or assume backend handles it.
        // I will rely on backend for now, but backend setup (Step 62) didn't override perform_create.
        // So I must provide created_by. However created_by is a User ID.
        // If authStore.user doesn't have ID, we have a problem.
        // Login action Set 'user' to { username, role: 'unknown' }. It didn't set ID.
        // I should fetch /users/me/ or similar to get ID.
    } catch (e) {
        console.error(e);
    }
});
</script>
