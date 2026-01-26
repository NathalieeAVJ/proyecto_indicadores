<template>
  <v-container fluid class="pa-0" style="height: calc(100vh - 64px);">
    <v-row no-gutters style="height: 100%;">
      <!-- SIDEBAR - Árbol de Carpetas -->
      <v-col cols="12" md="3" class="border-e" style="height: 100%; overflow-y: auto;">
        <v-card flat class="rounded-0">
          <v-card-title class="d-flex align-center pa-4 bg-grey-lighten-4">
            <v-icon class="mr-2" color="primary">mdi-folder-open</v-icon>
            <span class="text-h6">Carpetas</span>
            <v-spacer></v-spacer>
            <v-btn icon="mdi-folder-plus" size="small" color="primary" @click="openFolderDialog()"></v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-list density="compact" nav>
            <v-list-item
              prepend-icon="mdi-folder-home"
              title="Todos los Documentos"
              :active="selectedFolder === null"
              @click="selectFolder(null)"
            ></v-list-item>
            
            <v-divider class="my-2"></v-divider>
            
            <v-list-item
              v-for="folder in rootFolders"
              :key="folder.id"
              :prepend-icon="folder.icon || 'mdi-folder'"
              :title="folder.name"
              :active="selectedFolder?.id === folder.id"
              @click="selectFolder(folder)"
            >
              <template v-slot:append>
                <v-badge v-if="folder.document_count > 0" :content="folder.document_count" inline color="grey"></v-badge>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      
      <!-- ÁREA PRINCIPAL - Documentos -->
      <v-col cols="12" md="9" style="height: 100%; overflow-y: auto;">
        <v-card flat class="rounded-0">
          <!-- Toolbar -->
          <v-card-title class="d-flex align-center pa-4 bg-white border-b">
            <v-breadcrumbs :items="breadcrumbs" class="pa-0">
              <template v-slot:divider>
                <v-icon>mdi-chevron-right</v-icon>
              </template>
            </v-breadcrumbs>
            <v-spacer></v-spacer>
            <v-btn color="primary" prepend-icon="mdi-upload" variant="elevated" @click="openUploadDialog">
              Subir Documento
            </v-btn>
          </v-card-title>
          
          <!-- Barra de búsqueda y filtros -->
          <v-card-text class="pa-4 bg-grey-lighten-5 border-b">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="search"
                  prepend-inner-icon="mdi-magnify"
                  label="Buscar documentos..."
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="filterCategory"
                  :items="categories"
                  label="Filtrar por tipo"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                ></v-select>
              </v-col>
            </v-row>
          </v-card-text>
          
          <!-- Lista de Documentos -->
          <v-card-text class="pa-4">
            <v-data-table
              :headers="documentHeaders"
              :items="filteredDocuments"
              :loading="loading"
              :search="search"
              class="elevation-0"
            >
              <template v-slot:item.title="{ item }">
                <div class="d-flex align-center">
                  <v-icon class="mr-2" :color="getFileColor(item.file)">{{ getFileIcon(item.file) }}</v-icon>
                  <span class="font-weight-medium">{{ item.title }}</span>
                </div>
              </template>
              
              <template v-slot:item.category="{ item }">
                <v-chip size="small" variant="outlined" :color="getCategoryColor(item.category)">
                  {{ item.category_display }}
                </v-chip>
              </template>
              
              <template v-slot:item.version_number="{ item }">
                <v-chip size="x-small" color="info">v{{ item.version_number }}</v-chip>
              </template>
              
              <template v-slot:item.upload_date="{ item }">
                <span class="text-caption">{{ formatDate(item.upload_date) }}</span>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-eye" size="x-small" variant="text" color="primary" @click="viewDocument(item)"></v-btn>
                <v-btn icon="mdi-download" size="x-small" variant="text" color="secondary" @click="downloadDocument(item)"></v-btn>
                <v-btn icon="mdi-history" size="x-small" variant="text" color="info" @click="viewVersions(item)"></v-btn>
                <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click="deleteDocument(item)"></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- DIALOG: Nueva Carpeta -->
    <v-dialog v-model="folderDialog" max-width="500">
      <v-card class="rounded-xl">
        <v-card-title>Nueva Carpeta</v-card-title>
        <v-card-text>
          <v-form ref="folderFormRef">
            <v-text-field v-model="formFolder.name" label="Nombre de la Carpeta" variant="outlined" required></v-text-field>
            <v-textarea v-model="formFolder.description" label="Descripción" variant="outlined" rows="3"></v-textarea>
            <v-text-field v-model="formFolder.icon" label="Icono MDI" variant="outlined" placeholder="mdi-folder"></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="folderDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="elevated" @click="saveFolder" :loading="saving">Crear Carpeta</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- DIALOG: Subir Documento -->
    <v-dialog v-model="uploadDialog" max-width="700">
      <v-card class="rounded-xl">
        <v-card-title class="bg-primary text-white">Subir Nuevo Documento</v-card-title>
        <v-card-text class="pa-6">
          <v-form ref="uploadFormRef">
            <v-row>
              <v-col cols="12">
                <v-file-input
                  v-model="formDocument.file"
                  label="Seleccionar Archivo"
                  variant="outlined"
                  prepend-icon="mdi-paperclip"
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.png"
                  required
                ></v-file-input>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formDocument.title" label="Título del Documento" variant="outlined" required></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="formDocument.category"
                  :items="categories"
                  label="Categoría"
                  variant="outlined"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12">
                  <v-select
                    v-model="formDocument.folder"
                    :items="rootFolders"
                    item-title="name"
                    item-value="id"
                    label="Carpeta (opcional)"
                    variant="outlined"
                    clearable
                  ></v-select>
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="formDocument.description" label="Descripción" variant="outlined" rows="3"></v-textarea>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="formDocument.tags" label="Etiquetas (separadas por comas)" variant="outlined" placeholder="contrato, legal, 2024"></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4 bg-grey-lighten-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="uploadDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="elevated" @click="uploadDocument" :loading="saving">Subir</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- DIALOG: Ver Versiones -->
    <v-dialog v-model="versionsDialog" max-width="600">
      <v-card v-if="selectedDocument" class="rounded-xl">
        <v-card-title class="bg-info text-white">
          <v-icon class="mr-2">mdi-history</v-icon>
          Historial de Versiones: {{ selectedDocument.title }}
        </v-card-title>
        <v-card-text class="pa-0">
          <v-list>
            <v-list-item
              v-for="version in selectedDocument.versions"
              :key="version.id"
              :title="`Versión ${version.version_number}`"
              :subtitle="`Subido por ${version.uploaded_by_name} - ${formatDate(version.upload_date)}`"
            >
              <template v-slot:prepend>
                <v-avatar color="info-lighten-1">
                  <v-icon>mdi-file-document</v-icon>
                </v-avatar>
              </template>
              <template v-slot:append>
                <v-chip v-if="version.version_number === selectedDocument.version_number" color="success" size="small">Actual</v-chip>
              </template>
              <div v-if="version.notes" class="text-caption text-grey mt-1">{{ version.notes }}</div>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="versionsDialog = false">Cerrar</v-btn>
          <v-btn color="primary" prepend-icon="mdi-upload" @click="openNewVersionDialog">Nueva Versión</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- DIALOG: Nueva Versión -->
    <v-dialog v-model="newVersionDialog" max-width="500">
      <v-card class="rounded-xl">
        <v-card-title>Subir Nueva Versión</v-card-title>
        <v-card-text>
          <v-form ref="versionFormRef">
            <v-file-input
              v-model="newVersionFile"
              label="Seleccionar Archivo"
              variant="outlined"
              prepend-icon="mdi-file-upload"
              required
            ></v-file-input>
            <v-textarea
              v-model="newVersionNotes"
              label="Notas del Cambio"
              variant="outlined"
              rows="3"
              placeholder="Describe qué cambió en esta versión..."
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="newVersionDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="elevated" @click="uploadNewVersion" :loading="saving">Subir Versión</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';
import { formatDate } from '@/utils/format';

const loading = ref(false);
const saving = ref(false);
const search = ref('');
const filterCategory = ref(null);

const rootFolders = ref([]);
const documents = ref([]);
const selectedFolder = ref(null);
const selectedDocument = ref(null);

const folderDialog = ref(false);
const uploadDialog = ref(false);
const versionsDialog = ref(false);
const newVersionDialog = ref(false);

const formFolder = ref({ name: '', description: '', icon: 'mdi-folder', parent: null });
const formDocument = ref({ title: '', category: '', file: null, folder: null, description: '', tags: '' });
const newVersionFile = ref(null);
const newVersionNotes = ref('');

const categories = [
  { title: 'Contrato / Legal', value: 'contract' },
  { title: 'Factura / Comprobante', value: 'invoice' },
  { title: 'Plano / Técnico', value: 'blueprint' },
  { title: 'Documento Identidad', value: 'id_card' },
  { title: 'Certificado', value: 'certificate' },
  { title: 'Reporte / Informe', value: 'report' },
  { title: 'Manual / Procedimiento', value: 'manual' },
  { title: 'Otros Docs', value: 'other' },
];

const documentHeaders = [
  { title: 'Documento', key: 'title', sortable: true },
  { title: 'Tipo', key: 'category', align: 'center' },
  { title: 'Versión', key: 'version_number', align: 'center' },
  { title: 'Fecha', key: 'upload_date' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' },
];

const breadcrumbs = computed(() => {
  const items = [{ title: 'Documentos', disabled: false, to: '#' }];
  if (selectedFolder.value) {
    items.push({ title: selectedFolder.value.name, disabled: true });
  }
  return items;
});

const filteredDocuments = computed(() => {
  let result = documents.value;
  
  if (selectedFolder.value) {
    result = result.filter(d => d.folder === selectedFolder.value.id);
  }
  
  if (filterCategory.value) {
    result = result.filter(d => d.category === filterCategory.value);
  }
  
  return result;
});

const loadData = async () => {
  loading.value = true;
  try {
    const [foldersRes, docsRes] = await Promise.all([
      api.get('documentos/folders/?parent=null'),
      api.get('documentos/documents/')
    ]);
    rootFolders.value = foldersRes;
    documents.value = docsRes;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const selectFolder = (folder) => {
  selectedFolder.value = folder;
};

const openFolderDialog = () => {
  formFolder.value = { name: '', description: '', icon: 'mdi-folder', parent: selectedFolder.value?.id || null };
  folderDialog.value = true;
};

const saveFolder = async () => {
  saving.value = true;
  try {
    await api.post('documentos/folders/', formFolder.value);
    folderDialog.value = false;
    loadData();
  } catch (e) {
    alert('Error al crear carpeta');
  } finally {
    saving.value = false;
  }
};

const openUploadDialog = () => {
  formDocument.value = { title: '', category: '', file: null, folder: selectedFolder.value?.id || null, description: '', tags: '' };
  uploadDialog.value = true;
};

const uploadDocument = async () => {
  if (!formDocument.value.file || !formDocument.value.title) {
    alert('Por favor completa los campos requeridos');
    return;
  }
  
  saving.value = true;
  try {
    const formData = new FormData();
    const file = Array.isArray(formDocument.value.file) ? formDocument.value.file[0] : formDocument.value.file;
    if (file) formData.append('file', file);
    formData.append('title', formDocument.value.title);
    formData.append('category', formDocument.value.category);
    if (formDocument.value.folder) formData.append('folder', formDocument.value.folder);
    if (formDocument.value.description) formData.append('description', formDocument.value.description);
    if (formDocument.value.tags) formData.append('tags', formDocument.value.tags);
    
    await api.post('documentos/documents/', formData);
    
    uploadDialog.value = false;
    loadData();
  } catch (e) {
    console.error(e);
    alert('Error al subir documento');
  } finally {
    saving.value = false;
  }
};

const viewDocument = (doc) => {
  selectedDocument.value = doc;
  versionsDialog.value = true;
};

const viewVersions = (doc) => {
  selectedDocument.value = doc;
  versionsDialog.value = true;
};

const downloadDocument = async (doc) => {
  try {
    const response = await api.get(`documentos/documents/${doc.id}/download/`);
    if (response.file_url) {
      window.open(response.file_url, '_blank');
    }
  } catch (e) {
    alert('Error al descargar documento');
  }
};

const deleteDocument = async (doc) => {
  if (confirm(`¿Seguro que desea eliminar "${doc.title}"?`)) {
    try {
      await api.delete(`documentos/documents/${doc.id}/`);
      loadData();
    } catch (e) {
      alert('Error al eliminar documento');
    }
  }
};

const openNewVersionDialog = () => {
  newVersionFile.value = null;
  newVersionNotes.value = '';
  newVersionDialog.value = true;
};

const uploadNewVersion = async () => {
  if (!newVersionFile.value) {
    alert('Selecciona un archivo');
    return;
  }
  
  saving.value = true;
  try {
    const formData = new FormData();
    const file = Array.isArray(newVersionFile.value) ? newVersionFile.value[0] : newVersionFile.value;
    if (file) formData.append('file', file);
    formData.append('notes', newVersionNotes.value);
    
    await api.post(`documentos/documents/${selectedDocument.value.id}/upload_version/`, formData);
    
    newVersionDialog.value = false;
    versionsDialog.value = false;
    loadData();
  } catch (e) {
    alert('Error al subir nueva versión');
  } finally {
    saving.value = false;
  }
};

const getFileIcon = (filename) => {
  if (!filename) return 'mdi-file';
  const ext = filename.split('.').pop().toLowerCase();
  const iconMap = {
    pdf: 'mdi-file-pdf-box',
    doc: 'mdi-file-word',
    docx: 'mdi-file-word',
    xls: 'mdi-file-excel',
    xlsx: 'mdi-file-excel',
    jpg: 'mdi-file-image',
    png: 'mdi-file-image',
    zip: 'mdi-folder-zip',
  };
  return iconMap[ext] || 'mdi-file-document';
};

const getFileColor = (filename) => {
  if (!filename) return 'grey';
  const ext = filename.split('.').pop().toLowerCase();
  const colorMap = {
    pdf: 'red',
    doc: 'blue',
    docx: 'blue',
    xls: 'green',
    xlsx: 'green',
    jpg: 'purple',
    png: 'purple',
  };
  return colorMap[ext] || 'grey';
};

const getCategoryColor = (cat) => {
  const colorMap = {
    contract: 'blue',
    invoice: 'green',
    blueprint: 'purple',
    certificate: 'orange',
    report: 'indigo',
    manual: 'teal',
  };
  return colorMap[cat] || 'grey';
};

onMounted(loadData);
</script>

<style scoped>
.border-e {
  border-right: 1px solid #e0e0e0;
}
.border-b {
  border-bottom: 1px solid #e0e0e0;
}
</style>
