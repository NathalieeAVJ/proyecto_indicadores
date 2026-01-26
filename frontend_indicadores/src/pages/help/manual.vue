<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Centro de Ayuda y Manual de Usuario</h1>
        <p class="text-subtitle-1 text-grey">Documentación oficial del ecosistema NatTelf para la gestión de telecomunicaciones</p>
      </v-col>
    </v-row>

    <v-row>
      <!-- SIDEBAR NAVIGATION -->
      <v-col cols="12" md="3">
        <v-card variant="outlined" class="rounded-xl pa-2">
          <v-list density="compact" nav color="primary">
            <v-list-subheader class="text-uppercase font-weight-bold">Módulos del Sistema</v-list-subheader>
            <v-list-item 
              v-for="section in sections" 
              :key="section.id" 
              :active="activeSection === section.id"
              @click="activeSection = section.id"
              :prepend-icon="section.icon"
              :title="section.title"
              rounded="lg"
            ></v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- CONTENT AREA -->
      <v-col cols="12" md="9">
        <v-card elevation="2" class="rounded-xl pa-6 min-vh-75">
          <div v-if="currentSection">
            <div class="d-flex align-center mb-6">
              <v-icon size="42" color="primary" class="mr-4">{{ currentSection.icon }}</v-icon>
              <div>
                <h2 class="text-h4 font-weight-bold">{{ currentSection.title }}</h2>
                <p class="text-subtitle-2 text-grey">{{ currentSection.subtitle }}</p>
              </div>
            </div>

            <v-divider class="mb-6"></v-divider>

            <div v-for="(topic, idx) in currentSection.content" :key="idx" class="mb-8">
              <h3 class="text-h6 font-weight-bold mb-2 d-flex align-center">
                <v-icon start size="small" color="secondary">mdi-chevron-right-circle</v-icon>
                {{ topic.title }}
              </h3>
              <p class="text-body-1 text-grey-darken-2 mb-4">{{ topic.description }}</p>
              
              <v-alert
                v-if="topic.tip"
                density="compact"
                type="info"
                variant="tonal"
                class="mb-4 rounded-lg"
                prepend-icon="mdi-lightbulb"
              >
                <strong>Tip de NatTelf:</strong> {{ topic.tip }}
              </v-alert>

              <div v-if="topic.steps" class="bg-grey-lighten-4 pa-4 rounded-xl">
                <div class="text-subtitle-2 font-weight-bold mb-2">Procedimiento:</div>
                <div v-for="(step, sIdx) in topic.steps" :key="sIdx" class="d-flex align-start mb-2">
                  <v-avatar color="secondary" size="20" class="mr-2 text-caption font-weight-bold text-white">{{ sIdx + 1 }}</v-avatar>
                  <span class="text-body-2">{{ step }}</span>
                </div>
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue';

const activeSection = ref('incidents');

const sections = [
  {
    id: 'incidents',
    icon: 'mdi-alert-circle',
    title: 'Gestión de Incidencias',
    subtitle: 'Control de fallas en Telefonía y Radiobases',
    content: [
      {
        title: 'Registro de Incidencias (Tel)',
        description: 'Módulo para reportar fallas en líneas telefónicas específicas. Permite asociar la falla a un número y asignar un técnico responsable.',
        steps: [
          'Vaya a Gestión > Incidencias (Tel).',
          'Haga clic en el botón "Nueva Incidencia".',
          'Seleccione el número de teléfono afectado y el tipo de falla.',
          'Asigne un técnico y guarde el reporte.'
        ],
        tip: 'Las incidencias con estado "Terminado" pueden requerir la firma de una orden de trabajo para su cierre administrativo.'
      },
      {
        title: 'Tickets de Radiobases',
        description: 'Gestión técnica profunda para la infraestructura de antenas y estaciones base de la red.',
        steps: [
          'Acceda a Gestión > Tickets (Radios).',
          'Seleccione la Radiobase del mapa o lista.',
          'Documente el reporte técnico asignando prioridades.'
        ]
      }
    ]
  },
  {
    id: 'rrhh',
    icon: 'mdi-account-hard-hat',
    title: 'Recursos Humanos',
    subtitle: 'Nómina, Evaluación y Gestión de Talento',
    content: [
      {
        title: 'Censo de Empleados',
        description: 'Administración completa de los perfiles del trabajador: datos personales, familiares y jerarquía organizacional.',
        tip: 'Recuerde que ya no se borran empleados; se deben enviar a "Lista Negra" para conservar su historial.'
      },
      {
        title: 'Evaluación de Desempeño',
        description: 'Sistema mensual de calificación (1-100) con feedback cualitativo. Permite sugerir bonos por productividad.',
        steps: [
          'Entre al expediente del empleado.',
          'En la pestaña "Desempeño", haga clic en "Evaluar Mes".',
          'Asigne el puntaje y justifique el incentivo sugerido.'
        ]
      },
      {
        title: 'Gestión de Lista Negra',
        description: 'Módulo de auditoría para ex-empleados. Conserva la memoria de por qué se desincorporó un personal.',
        tip: 'Desde aquí puede re-contratar a un ex-empleado restaurando su perfil con un solo clic.'
      }
    ]
  },
  {
    id: 'inventory',
    icon: 'mdi-warehouse',
    title: 'Inventario y Activos',
    subtitle: 'Almacén de Repuestos y Herramientas',
    content: [
      {
        title: 'Inventario Global de Activos',
        description: 'Control de Laptops, Celulares y Herramientas asignadas al personal o en stock.',
        steps: [
          'Vaya a Inventario > Activos y Equipos.',
          'Use el buscador para localizar un equipo por código NT- o Serial.',
          'Asigne o retire de cargo un equipo a un trabajador.'
        ]
      },
      {
        title: 'Bitácora Técnica (Mantenimiento)',
        description: 'Historial de reparaciones por equipo. Registra costos y descripciones del servicio técnico.',
        tip: 'Consulte siempre el historial antes de aprobar la compra de un equipo nuevo para evaluar si el actual es reparable.'
      },
      {
        title: 'Almacén de Repuestos',
        description: 'Control de piezas para reparaciones de red. Actualización de stock en tiempo real al cerrar incidencias.'
      }
    ]
  },
  {
    id: 'selfservice',
    icon: 'mdi-account-details',
    title: 'Autogestión (Usuario)',
    subtitle: 'Portal personal del trabajador logueado',
    content: [
      {
        title: 'Mis Trámites',
        description: 'Espacio privado para que el trabajador gestione su relación con la empresa desde su menú de perfil.',
        steps: [
          'Haga clic en su Avatar (arriba a la derecha).',
          'Seleccione "Mis Trámites".',
          'Consulte sus pagos, vacaciones o reporte fallas de sus equipos asignados.'
        ],
        tip: 'El reporte de fallas de equipo inicia un trámite automático con el departamento técnico de NatTelf.'
      }
    ]
  },
  {
    id: 'administration',
    icon: 'mdi-shield-check',
    title: 'Auditoría y Seguridad',
    subtitle: 'Supervisión de trazabilidad y accesos',
    content: [
      {
        title: 'Audit Logs (Trazabilidad)',
        description: 'Registro irrefutable de quién hizo qué en el sistema. Crucial para supervisar cambios en nómina, inventario y desincorporaciones.',
        tip: 'Cada movimiento a Lista Negra genera una alerta automática por acá.'
      },
      {
        title: 'Gestión de Sesiones',
        description: 'El sistema cierra sesión automáticamente tras 1 hora de inactividad por seguridad bancaria/institucional.'
      }
    ]
  }
];

const currentSection = computed(() => sections.find(s => s.id === activeSection.value));
</script>

<style scoped>
.min-vh-75 { min-height: 75vh; }
</style>
