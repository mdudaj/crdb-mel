<script setup lang="ts">
withDefaults(defineProps<{
  title?: string;
  span?: 2 | 3 | 4 | 5 | 6 | 7 | 8 | 12;
  rowSpan?: 1 | 2;
  variant?: 'default' | 'goal';
}>(), {
  title: undefined,
  span: 4,
  rowSpan: 1,
  variant: 'default',
});
</script>

<template>
  <article
    class="dashboard-card"
    :class="[
      `dashboard-card--span-${span}`,
      rowSpan === 2 ? 'dashboard-card--row-span-2' : '',
      variant === 'goal' ? 'dashboard-card--goal' : '',
    ]"
  >
    <header v-if="title || $slots.header" class="dashboard-card__header">
      <slot name="header">
        <h2>{{ title }}</h2>
      </slot>
    </header>
    <div class="dashboard-card__content">
      <slot />
    </div>
    <footer v-if="$slots.footer" class="dashboard-card__footer">
      <slot name="footer" />
    </footer>
  </article>
</template>

<style scoped>
.dashboard-card {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: var(--dash-space-3, 12px);
  min-width: 0;
  min-height: 196px;
  padding: var(--dash-space-4, 16px);
  border: 1px solid var(--dash-border, #E3E8E5);
  border-radius: 12px;
  background: var(--dash-surface, #FFFFFF);
  box-shadow: 0 8px 18px rgba(6, 78, 59, 0.06);
}

.dashboard-card__header,
.dashboard-card__footer {
  min-width: 0;
}

.dashboard-card__content {
  display: grid;
  gap: var(--dash-space-3, 12px);
  align-content: start;
  min-width: 0;
}

.dashboard-card__footer {
  display: flex;
  align-items: center;
  min-height: 24px;
  margin-top: auto;
}

.dashboard-card__header h2 {
  margin: 0;
  color: var(--dash-text, #17211C);
  font-size: 0.98rem;
  white-space: nowrap;
}

.dashboard-card--span-2 { grid-column: span 2; }
.dashboard-card--span-3 { grid-column: span 3; }
.dashboard-card--span-4 { grid-column: span 4; }
.dashboard-card--span-5 { grid-column: span 5; }
.dashboard-card--span-6 { grid-column: span 6; }
.dashboard-card--span-7 { grid-column: span 7; }
.dashboard-card--span-8 { grid-column: span 8; }
.dashboard-card--span-12 { grid-column: span 12; }

.dashboard-card--row-span-2 {
  grid-row: span 2;
  min-height: 470px;
}

.dashboard-card--goal {
  overflow: hidden;
  min-height: 260px;
  background: linear-gradient(180deg, #FFFFFF 0%, #EAF7EE 58%, #DDF2E4 100%);
}

@media (max-width: 1279px) {
  .dashboard-card--span-2,
  .dashboard-card--span-3,
  .dashboard-card--span-4,
  .dashboard-card--span-5,
  .dashboard-card--span-6,
  .dashboard-card--span-7,
  .dashboard-card--span-8 {
    grid-column: span 6;
  }

  .dashboard-card--span-12,
  .dashboard-card--row-span-2 {
    grid-column: span 12;
  }
}

@media (max-width: 599px) {
  .dashboard-card,
  .dashboard-card--span-2,
  .dashboard-card--span-3,
  .dashboard-card--span-4,
  .dashboard-card--span-5,
  .dashboard-card--span-6,
  .dashboard-card--span-7,
  .dashboard-card--span-8,
  .dashboard-card--span-12,
  .dashboard-card--row-span-2 {
    grid-column: span 1;
  }
}
</style>
