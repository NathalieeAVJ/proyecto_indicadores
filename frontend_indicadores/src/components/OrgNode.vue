<template>
  <div class="node-wrapper d-flex flex-column align-center">
    <!-- Card Node -->
    <v-card 
      width="240" 
      class="node-card mb-10 rounded-xl" 
      @click="$emit('select', node)"
      :style="nodeStyles"
    >
      <!-- Top Glowing Bar -->
      <div class="glow-bar" :style="{ background: `linear-gradient(90deg, transparent, ${getRankColor(node.manager_detail?.rank)}, transparent)` }"></div>
      
      <v-card-text class="pa-5 text-center position-relative">
        <div class="avatar-wrapper mb-4">
          <v-avatar 
            size="70" 
            class="node-avatar-premium"
            :style="{ 
              background: `linear-gradient(135deg, white 0%, ${getRankColor(node.manager_detail?.rank)}33 100%)`,
              boxShadow: `0 0 25px ${getRankColor(node.manager_detail?.rank)}44`
            }"
          >
            <v-icon :color="getRankColor(node.manager_detail?.rank)" size="36" class="rank-icon-animate">
              {{ getRankIcon(node.manager_detail?.rank) }}
            </v-icon>
          </v-avatar>
          <div class="avatar-ring" :style="{ borderColor: getRankColor(node.manager_detail?.rank) + '44' }"></div>
        </div>
        
        <div class="text-h6 font-weight-black node-title-modern">
          {{ node.name }}
        </div>
        
        <div class="text-caption font-weight-bold text-grey-darken-3 manager-label mt-1 mb-4">
          <v-icon size="12" class="mr-1">mdi-account-star</v-icon>
          {{ node.manager_detail?.full_name || 'Líder por asignar' }}
        </div>

        <div class="staff-chip-modern px-4 py-1 rounded-pill" :style="{ border: `1px solid ${getRankColor(node.manager_detail?.rank)}22` }">
          <span class="text-overline font-weight-black mr-2">EQUIPO</span>
          <span class="text-h6 font-weight-black" :style="{ color: getRankColor(node.manager_detail?.rank) }">{{ node.staff_count }}</span>
        </div>
      </v-card-text>
    </v-card>

    <!-- Tech-Style Connectors -->
    <div v-if="children.length" class="children-container-tech d-flex flex-row justify-center">
      <div v-for="child in children" :key="child.id" class="child-branch-tech px-4">
        <div class="connector-vertical-tech" :style="{ background: `linear-gradient(to bottom, #D1C4E9, ${getRankColor(node.manager_detail?.rank)}aa)` }">
          <div class="pulse-dot"></div>
        </div>
        <OrgNode :node="child" :all-deps="allDeps" @select="$emit('select', $event)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  node: Object,
  allDeps: Array
});

const emit = defineEmits(['select']);

const children = computed(() => {
  return props.allDeps.filter(d => d.parent === props.node.id);
});

const nodeStyles = computed(() => {
  const color = getRankColor(props.node.manager_detail?.rank);
  return {
    background: 'rgba(255, 255, 255, 0.95)',
    border: `1px solid ${color}22`,
    boxShadow: `0 20px 40px -15px ${color}33`,
  };
});

const getRankColor = (rank) => {
  const colors = {
    0: '#6200EA', // Presidencia (Deep Purple Glow)
    1: '#00B0FF', // VP (Vibrant Blue)
    2: '#00E676', // Gnte Gral (Neon Green)
    3: '#FF9100', // Gerente (Vivid Orange)
    4: '#00E5FF', // Coord (Electric Cyan)
    5: '#78909C'  // Operativo
  };
  return colors[rank] || '#BDBDBD';
};

const getRankIcon = (rank) => {
  if (rank === 0) return 'mdi-crown';
  if (rank === 1) return 'mdi-layers-triple';
  if (rank === 2) return 'mdi-shield-crown-outline';
  if (rank === 3) return 'mdi-star-face';
  return 'mdi-hexagon-multiple';
};
</script>

<style scoped>
.node-card {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  z-index: 5;
}

.node-card:hover {
  transform: translateY(-15px) scale(1.08);
  background: #ffffff !important;
  box-shadow: 0 30px 60px -12px rgba(50, 50, 93, 0.25), 0 18px 36px -18px rgba(0, 0, 0, 0.3) !important;
}

.glow-bar {
  height: 4px;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0.8;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.avatar-ring {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border: 2px dashed;
  border-radius: 50%;
  animation: rotate-ring 10s linear infinite;
}

@keyframes rotate-ring {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.node-avatar-premium {
  border: 4px solid white;
  transition: transform 0.3s;
}

.node-card:hover .node-avatar-premium {
  transform: scale(1.1);
}

.node-title-modern {
  color: #0D47A1;
  text-transform: uppercase;
  letter-spacing: 1px;
  line-height: 1.2;
}

.manager-label {
  letter-spacing: 0.5px;
  opacity: 0.8;
}

.staff-chip-modern {
  display: inline-flex;
  align-items: center;
  background: #f8faff;
  transition: all 0.3s;
}

.node-card:hover .staff-chip-modern {
  background: #EEF2FF;
  transform: scale(1.05);
}

/* Technical Connectors */
.connector-vertical-tech {
  width: 3px;
  height: 40px;
  margin-bottom: 4px;
  position: relative;
  border-radius: 2px;
}

.pulse-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 0 10px rgba(255,255,255,0.8);
  animation: tech-pulse 2s infinite ease-in-out;
}

@keyframes tech-pulse {
  0% { top: 0; opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.children-container-tech {
  position: relative;
  border-top: 3px solid #D1C4E9;
  margin-top: -20px;
  padding-top: 20px;
  border-radius: 30px 30px 0 0;
}

.child-branch-tech {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.child-branch-tech::before {
  content: '';
  position: absolute;
  top: -3px;
  left: 50%;
  width: 3px;
  height: 20px;
  background: #D1C4E9;
  transform: translateX(-50%);
}

.rank-icon-animate {
  animation: float-icon 4s infinite ease-in-out;
}

@keyframes float-icon {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
</style>
