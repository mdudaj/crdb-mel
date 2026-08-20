<template>
  <section class="dashboard-page" aria-label="TACATDP dashboard visualization">
    <slot />
  </section>
</template>

<style scoped>
.dashboard-page {
  --dash-dark: #064E3B;
  --dash-primary: #15803D;
  --dash-positive: #16A34A;
  --dash-bg: #F5F7F6;
  --dash-surface: #FFFFFF;
  --dash-text: #17211C;
  --dash-muted: #64706A;
  --dash-border: #E3E8E5;
  --dash-space-1: 4px;
  --dash-space-2: 8px;
  --dash-space-3: 12px;
  --dash-space-4: 16px;
  --dash-space-5: 24px;
  --dash-space-6: 32px;
  display: grid;
  gap: var(--dash-space-4);
  min-height: calc(100vh - 112px);
  padding: var(--dash-space-4);
  background: var(--dash-bg);
  color: var(--dash-text);
}

@media (min-width: 840px) {
  .dashboard-page {
    padding: var(--dash-space-5);
    gap: var(--dash-space-5);
  }
}

@media (max-width: 599px) {
  .dashboard-page {
    padding: var(--dash-space-3);
  }
}
</style>
