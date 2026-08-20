<script setup lang="ts">
import type { Component } from 'vue';

withDefaults(defineProps<{
  label: string;
  value: string;
  change: string;
  tone?: 'green' | 'blue' | 'amber' | 'purple';
  icon: Component;
}>(), {
  tone: 'green',
});
</script>

<template>
  <article class="kpi-card" :class="`kpi-card--${tone}`">
    <span class="kpi-card__icon" :class="`kpi-card__icon--${tone}`">
      <component :is="icon" aria-hidden="true" />
    </span>
    <div>
      <span>{{ label }}</span>
      <strong>{{ value }}</strong>
      <small>↑ {{ change }}</small>
    </div>
  </article>
</template>

<style scoped>
.kpi-card {
  --kpi-card-accent: #15803D;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: var(--dash-space-3, 12px);
  min-width: 0;
  min-height: 104px;
  padding: var(--dash-space-4, 16px);
  border: 1px solid var(--dash-border, #E3E8E5);
  border-radius: 12px;
  background: var(--dash-surface, #FFFFFF);
  box-shadow: 0 8px 18px rgba(6, 78, 59, 0.06);
}

.kpi-card::before {
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--kpi-card-accent) 82%, #FFFFFF), var(--kpi-card-accent));
  content: "";
}

.kpi-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 48px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
}

.kpi-card__icon svg {
  width: 22px;
  height: 22px;
}

.kpi-card--green { --kpi-card-accent: #15803D; }
.kpi-card--blue { --kpi-card-accent: #2563EB; }
.kpi-card--amber { --kpi-card-accent: #F59E0B; }
.kpi-card--purple { --kpi-card-accent: #7C3AED; }

.kpi-card__icon--green { background: #EAF7EE; color: #15803D; }
.kpi-card__icon--blue { background: #DBEAFE; color: #2563EB; }
.kpi-card__icon--amber { background: #FEF3C7; color: #B45309; }
.kpi-card__icon--purple { background: #EDE9FE; color: #7C3AED; }

.kpi-card > div {
  min-width: 0;
}

.kpi-card span,
.kpi-card small,
.kpi-card strong {
  display: block;
  white-space: nowrap;
}

.kpi-card span,
.kpi-card small {
  font-size: 0.72rem;
}

.kpi-card strong {
  margin: var(--dash-space-2, 8px) 0;
  font-size: clamp(1.14rem, 1.35vw, 1.36rem);
  letter-spacing: -0.03em;
}

.kpi-card small {
  color: #15803D;
  font-weight: 700;
}
</style>
