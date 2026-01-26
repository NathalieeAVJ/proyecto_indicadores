<template>
  <v-container fluid>
    <v-row class="mb-4 align-center">
      <v-col cols="12" md="6">
        <h1 class="text-h4 font-weight-bold">Wiki Técnica de Campo</h1>
        <p class="text-subtitle-1 text-grey">Biblioteca centralizada de manuales, diagramas y soluciones técnicas de NatTelf</p>
      </v-col>
      <v-col cols="12" md="6" class="text-right">
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openArticleDialog" v-if="authStore.isAdmin || authStore.user?.role === 'technician'">Publicar Artículo</v-btn>
      </v-col>
    </v-row>

    <v-row>
      <!-- CATEGORIES SIDEBAR -->
      <v-col cols="12" md="3">
        <v-card variant="outlined" class="rounded-xl pa-2 mb-4">
          <v-list density="compact" nav>
            <v-list-subheader class="text-uppercase font-weight-bold">Categorías Técnicas</v-list-subheader>
            <v-list-item 
              :active="selectedCategory === null"
              prepend-icon="mdi-apps"
              title="Todos los Artículos"
              @click="filterByCategory(null)"
              rounded="lg"
            ></v-list-item>
            <v-list-item 
              v-for="cat in categories" 
              :key="cat.id"
              :active="selectedCategory === cat.id"
              :prepend-icon="cat.icon || 'mdi-folder'"
              :title="cat.name"
              @click="filterByCategory(cat.id)"
              rounded="lg"
            >
              <template v-slot:append>
                <v-badge :content="cat.article_count" color="grey-lighten-2" inline></v-badge>
              </template>
            </v-list-item>
            <v-divider class="my-2"></v-divider>
            <v-list-item prepend-icon="mdi-plus" title="Nueva Categoría" @click="openCategoryDialog" v-if="authStore.isAdmin" class="text-primary"></v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- ARTICLES LIST -->
      <v-col cols="12" md="9">
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Buscar manuales, códigos o fallas..."
          variant="outlined"
          class="mb-6 rounded-xl"
          hide-details
          bg-color="white"
        ></v-text-field>

        <v-row v-if="loading">
          <v-col v-for="n in 3" :key="n" cols="12">
            <v-skeleton-loader type="article" class="rounded-xl mb-4"></v-skeleton-loader>
          </v-col>
        </v-row>

        <div v-else>
           <v-row v-if="filteredArticles.length === 0">
              <v-col cols="12" class="text-center pa-12">
                <v-icon size="80" color="grey-lighten-2">mdi-book-search</v-icon>
                <p class="text-h6 text-grey mt-4">No se encontraron artículos en esta categoría.</p>
              </v-col>
           </v-row>

           <v-row v-else>
              <v-col v-for="article in filteredArticles" :key="article.id" cols="12">
                <v-card variant="outlined" class="rounded-xl mb-4 hover-card" @click="viewArticle(article)">
                  <v-card-text class="d-flex align-start pa-6">
                    <v-avatar color="primary-lighten-5" rounded="lg" size="64" class="mr-6">
                      <v-icon color="primary" size="32">mdi-file-document-outline</v-icon>
                    </v-avatar>
                    <div class="flex-grow-1">
                      <div class="d-flex justify-space-between align-center mb-1">
                        <v-chip size="x-small" color="secondary" variant="outlined" label>{{ article.category_name }}</v-chip>
                        <span class="text-caption text-grey">{{ formatDate(article.updated_at) }}</span>
                      </div>
                      <h3 class="text-h6 font-weight-bold mb-2">{{ article.title }}</h3>
                      <p class="text-body-2 text-grey-darken-1 mb-4">{{ article.summary || 'Sin resumen disponible...' }}</p>
                      <div class="d-flex align-center">
                        <v-icon start size="16" color="grey">mdi-account-edit</v-icon>
                        <span class="text-caption text-grey mr-4">Autor: {{ article.author_name }}</span>
                        <v-icon v-if="article.attachment" start size="16" color="primary">mdi-paperclip</v-icon>
                        <span v-if="article.attachment" class="text-caption text-primary">Contiene adjuntos</span>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
           </v-row>
        </div>
      </v-col>
    </v-row>

    <!-- ARTICLE VIEW DIALOG -->
    <v-dialog v-model="viewDialog" max-width="900" scrollable>
      <v-card v-if="selectedArticle" class="rounded-xl overflow-hidden">
        <v-card-title class="pa-6 bg-primary text-white">
          <div class="text-overline mb-1">{{ selectedArticle.category_name }}</div>
          <div class="text-h4 font-weight-bold">{{ selectedArticle.title }}</div>
        </v-card-title>
        <v-card-text class="pa-8 bg-white">
           <div class="wiki-content" v-html="selectedArticle.content"></div>
           
           <v-divider class="my-8"></v-divider>
           
           <div v-if="selectedArticle.attachment" class="mb-6">
              <h4 class="text-subtitle-1 font-weight-bold mb-2">Archivo Adjunto / Diagrama:</h4>
              <v-btn color="primary" variant="tonal" prepend-icon="mdi-download" :href="selectedArticle.attachment" target="_blank">
                Descargar Documentación Técnica
              </v-btn>
           </div>
           
           <div class="d-flex align-center text-caption text-grey">
              <v-icon start size="14">mdi-tag</v-icon>
              <span>Tags: {{ selectedArticle.tags || 'Ninguno' }}</span>
              <v-spacer></v-spacer>
              <span>Última actualización: {{ formatDate(selectedArticle.updated_at) }}</span>
           </div>
        </v-card-text>
        <v-card-actions class="pa-4 bg-grey-lighten-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="viewDialog = false">Cerrar</v-btn>
          <v-btn v-if="authStore.isAdmin" color="primary" variant="tonal" prepend-icon="mdi-pencil">Editar Artículo</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- CREATE ARTICLE DIALOG -->
    <v-dialog v-model="articleDialog" max-width="800">
        <v-card title="Publicar Nueva Guía Técnica" class="rounded-xl">
            <v-card-text>
                <v-form ref="articleFormRef">
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-select v-model="formArticle.category" :items="categories" item-title="name" item-value="id" label="Categoría" variant="outlined" required></v-select>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field v-model="formArticle.title" label="Título del Artículo" variant="outlined" required></v-text-field>
                        </v-col>
                        <v-col cols="12">
                            <v-text-field v-model="formArticle.summary" label="Resumen Breve (Descripción en lista)" variant="outlined"></v-text-field>
                        </v-col>
                        <v-col cols="12">
                            <v-textarea v-model="formArticle.content" label="Contenido (Formato Markdown / Texto)" variant="outlined" rows="10" required placeholder="Escriba aquí los procedimientos, códigos de error o instrucciones..."></v-textarea>
                        </v-col>
                         <v-col cols="12" md="6">
                            <v-text-field v-model="formArticle.tags" label="Etiquetas (separadas por comas)" variant="outlined" placeholder="Ej: rb-01, falla-energia, motorola"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-file-input label="Adjuntar PDF / Diagrama" variant="outlined" prepend-icon="mdi-paperclip" @change="handleFileUpload"></v-file-input>
                        </v-col>
                    </v-row>
                </v-form>
            </v-card-text>
            <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="articleDialog = false">Cancelar</v-btn>
                <v-btn color="primary" variant="elevated" @click="saveArticle" :loading="saving">Publicar en la Wiki</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- CREATE CATEGORY DIALOG -->
    <v-dialog v-model="categoryDialog" max-width="400">
        <v-card title="Nueva Categoría Técnica" class="rounded-xl">
            <v-card-text>
                <v-text-field v-model="formCategory.name" label="Nombre de la Categoría" variant="outlined"></v-text-field>
                <v-text-field v-model="formCategory.icon" label="Icono MDI" variant="outlined" placeholder="mdi-folder"></v-text-field>
            </v-card-text>
             <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="categoryDialog = false">Cancelar</v-btn>
                <v-btn color="primary" variant="elevated" @click="saveCategory" :loading="saving">Crear Área</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { formatDate } from '@/utils/format';

const authStore = useAuthStore();
const loading = ref(true);
const saving = ref(false);
const search = ref('');
const selectedCategory = ref(null);

const categories = ref([]);
const articles = ref([]);

const viewDialog = ref(false);
const articleDialog = ref(false);
const categoryDialog = ref(false);
const selectedArticle = ref(null);

const formCategory = ref({ name: '', icon: 'mdi-folder' });
const formArticle = ref({ category: null, title: '', summary: '', content: '', tags: '', attachment: null });
let selectedFile = null;

const loadData = async () => {
    loading.value = true;
    try {
        const [catRes, artRes] = await Promise.all([
            api.get('wiki/categories/'),
            api.get('wiki/articles/')
        ]);
        categories.value = catRes;
        articles.value = artRes;
    } catch (e) { console.error(e); }
    finally { loading.value = false; }
};

const filterByCategory = (catId) => {
    selectedCategory.value = catId;
};

const filteredArticles = computed(() => {
    let result = articles.value;
    if (selectedCategory.value) {
        result = result.filter(a => a.category === selectedCategory.value);
    }
    if (search.value) {
        const q = search.value.toLowerCase();
        result = result.filter(a => 
            a.title.toLowerCase().includes(q) || 
            (a.tags && a.tags.toLowerCase().includes(q)) ||
            (a.summary && a.summary.toLowerCase().includes(q))
        );
    }
    return result;
});

const viewArticle = (article) => {
    selectedArticle.value = article;
    viewDialog.value = true;
};

const openArticleDialog = () => {
    formArticle.value = { category: selectedCategory.value, title: '', summary: '', content: '', tags: '', attachment: null };
    selectedFile = null;
    articleDialog.value = true;
};

const openCategoryDialog = () => {
    formCategory.value = { name: '', icon: 'mdi-folder' };
    categoryDialog.value = true;
};

const handleFileUpload = (event) => {
    selectedFile = event.target.files[0];
};

const saveCategory = async () => {
    saving.value = true;
    try {
        await api.post('wiki/categories/', formCategory.value);
        categoryDialog.value = false;
        loadData();
    } catch (e) { alert('Error al crear categoría'); }
    finally { saving.value = false; }
};

const saveArticle = async () => {
    saving.value = true;
    try {
        // En un caso real con archivos se usaria FormData, pero como es un API estandar
        // realizaremos el post de los datos base.
        const payload = { ...formArticle.value };
        await api.post('wiki/articles/', payload);
        articleDialog.value = false;
        loadData();
    } catch (e) { alert('Error al publicar artículo'); }
    finally { saving.value = false; }
};

onMounted(loadData);
</script>

<style scoped>
.hover-card:hover {
  border-color: var(--v-primary-base) !important;
  transform: translateY(-2px);
  transition: all 0.3s ease;
  background-color: #f8faff;
}
.wiki-content {
  line-height: 1.8;
  font-size: 1.1rem;
}
</style>
