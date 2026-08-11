<script setup lang="ts">
withDefaults(defineProps<{
  as?: 'article' | 'section' | 'div';
  accent?: 'green' | 'blue' | 'amber' | 'purple' | 'red' | 'neutral';
}>(), {
  as: 'section',
  accent: 'green',
});
</script>

<template>
  <component :is="as" class="surface-card" :class="`surface-card--${accent}`">
    <slot />
  </component>
</template>

<style scoped>
.surface-card {
  --surface-card-accent: #15803D;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--m3-outline, var(--dash-border, #E3E8E5));
  border-radius: 16px;
  background: var(--m3-surface, var(--dash-surface, #FFFFFF));
  box-shadow: 0 8px 18px rgba(6, 78, 59, 0.06);
}

.surface-card::before {
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--surface-card-accent) 82%, #FFFFFF), var(--surface-card-accent));
  content: "";
}

.surface-card--green { --surface-card-accent: #15803D; }
.surface-card--blue { --surface-card-accent: #2563EB; }
.surface-card--amber { --surface-card-accent: #F59E0B; }
.surface-card--purple { --surface-card-accent: #7C3AED; }
.surface-card--red { --surface-card-accent: #DC2626; }
.surface-card--neutral { --surface-card-accent: #9CA3AF; }
</style>
