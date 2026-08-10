export interface KpiMetric {
  id: string;
  label: string;
  value: string;
  change: string;
  icon: string;
  tone: 'green' | 'blue' | 'amber' | 'purple';
}

export interface NamedValue {
  name: string;
  value: number;
  percent?: number;
  color?: string;
  amount?: string;
}

export interface TrendPoint {
  month: string;
  value: number;
  label: string;
}

export interface RegionMetric {
  name: string;
  disbursed: number;
  disbursedLabel: string;
  loans: number;
  borrowers: number;
  repaymentRate: string;
  farmersTrained: number;
  technologies: string[];
  submissionCompleteness: string;
}

export interface OutcomeMetric {
  label: string;
  value: string;
  change: string;
  icon: string;
  tone: 'blue' | 'green' | 'amber' | 'teal';
  definition: string;
}

export interface RecentSubmission {
  region: string;
  period: string;
  status: 'Submitted' | 'Under review' | 'Approved' | 'Returned' | 'Overdue' | 'Incomplete';
  time: string;
}

export const dashboardKpis: KpiMetric[] = [
  { id: 'active-loans', label: 'Active Loans', value: '12,458', change: '+14% vs Apr', icon: 'leaf', tone: 'green' },
  { id: 'active-borrowers', label: 'Active Borrowers', value: '18,732', change: '+11% vs Apr', icon: 'group', tone: 'green' },
  { id: 'total-disbursed', label: 'Total Disbursed', value: 'TZS 152.6B', change: '+16% vs Apr', icon: 'finance', tone: 'blue' },
  { id: 'repayment-rate', label: 'Repayment Rate', value: '93%', change: '+3pp vs Apr', icon: 'repayment', tone: 'amber' },
  { id: 'farmers-trained', label: 'Farmers Trained', value: '8,452', change: '+21% vs Apr', icon: 'sprout', tone: 'green' },
  { id: 'carbon-avoided', label: 'tCO₂e Avoided', value: '32,184', change: '+19% vs Apr', icon: 'co2', tone: 'purple' },
];

export const loanPortfolio: NamedValue[] = [
  { name: 'Short-term (Post-harvest)', value: 6142, percent: 49, color: '#16A34A', amount: 'TZS 61.4B' },
  { name: 'Medium-term', value: 3876, percent: 31, color: '#2563EB', amount: 'TZS 52.1B' },
  { name: 'Long-term', value: 2440, percent: 20, color: '#F59E0B', amount: 'TZS 39.1B' },
];

export const disbursementTrend: TrendPoint[] = [
  { month: 'Jan', value: 78.4, label: '78.4B' },
  { month: 'Feb', value: 92.8, label: '92.8B' },
  { month: 'Mar', value: 116.5, label: '116.5B' },
  { month: 'Apr', value: 131.4, label: '131.4B' },
  { month: 'May', value: 152.6, label: '152.6B' },
];

export const technologyFinancing: NamedValue[] = [
  { name: 'Solar-powered irrigation pumps', value: 2874, percent: 23 },
  { name: 'Water Harvesting (Reservoirs)', value: 2156, percent: 17 },
  { name: 'Greenhouses', value: 1842, percent: 15 },
  { name: 'Organic Fertilizer', value: 1536, percent: 12 },
  { name: 'Drought-resistant Seeds', value: 1328, percent: 11 },
  { name: 'Other Practices', value: 722, percent: 6 },
];

export const loanPerformance: NamedValue[] = [
  { name: 'Performing', value: 11584, percent: 93, color: '#16A34A', amount: 'TZS 141.8B' },
  { name: 'At Risk', value: 542, percent: 4, color: '#F59E0B', amount: 'TZS 6.8B' },
  { name: 'Non-Performing', value: 332, percent: 3, color: '#DC2626', amount: 'TZS 4.0B' },
];

export const regionalMetrics: RegionMetric[] = [
  { name: 'Morogoro', disbursed: 21.8, disbursedLabel: 'TZS 21.8B', loans: 1842, borrowers: 2460, repaymentRate: '94%', farmersTrained: 1240, technologies: ['Solar irrigation', 'Reservoirs', 'Organic fertilizer'], submissionCompleteness: '98%' },
  { name: 'Pwani', disbursed: 16.4, disbursedLabel: 'TZS 16.4B', loans: 1210, borrowers: 1724, repaymentRate: '92%', farmersTrained: 860, technologies: ['Warehouses', 'Drip irrigation'], submissionCompleteness: '94%' },
  { name: 'Dodoma', disbursed: 12.6, disbursedLabel: 'TZS 12.6B', loans: 1038, borrowers: 1510, repaymentRate: '91%', farmersTrained: 740, technologies: ['Drought-resistant seeds', 'Terracing'], submissionCompleteness: '91%' },
  { name: 'Mwanza', disbursed: 9.8, disbursedLabel: 'TZS 9.8B', loans: 842, borrowers: 1194, repaymentRate: '93%', farmersTrained: 632, technologies: ['Greenhouses', 'Water harvesting'], submissionCompleteness: '96%' },
  { name: 'Kagera', disbursed: 6.7, disbursedLabel: 'TZS 6.7B', loans: 614, borrowers: 880, repaymentRate: '90%', farmersTrained: 470, technologies: ['Mulching', 'Crop rotation'], submissionCompleteness: '89%' },
  { name: 'Arusha', disbursed: 5.8, disbursedLabel: 'TZS 5.8B', loans: 522, borrowers: 744, repaymentRate: '95%', farmersTrained: 410, technologies: ['Greenhouses', 'Hydroponics'], submissionCompleteness: '93%' },
  { name: 'Kilimanjaro', disbursed: 4.9, disbursedLabel: 'TZS 4.9B', loans: 488, borrowers: 706, repaymentRate: '96%', farmersTrained: 392, technologies: ['Solar irrigation', 'Organic fertilizer'], submissionCompleteness: '95%' },
  { name: 'Mbeya', disbursed: 3.6, disbursedLabel: 'TZS 3.6B', loans: 328, borrowers: 520, repaymentRate: '90%', farmersTrained: 284, technologies: ['Improved irrigation', 'Drought-resistant seeds'], submissionCompleteness: '86%' },
  { name: 'Iringa', disbursed: 2.9, disbursedLabel: 'TZS 2.9B', loans: 260, borrowers: 418, repaymentRate: '89%', farmersTrained: 214, technologies: ['Terracing', 'Windbreak trees'], submissionCompleteness: '84%' },
  { name: 'Lindi', disbursed: 0.8, disbursedLabel: 'TZS 0.8B', loans: 74, borrowers: 120, repaymentRate: '88%', farmersTrained: 66, technologies: ['Mixed cropping'], submissionCompleteness: '76%' },
];

export const climateOutcomes: OutcomeMetric[] = [
  { label: 'Area Under Improved Practices (ha)', value: '26,842', change: '+18% vs Apr', icon: 'water', tone: 'blue', definition: 'Prototype hectares reported under improved climate-smart practices for the selected period.' },
  { label: 'Yield Increase (Avg %)', value: '28%', change: '+6pp vs Apr', icon: 'growth', tone: 'green', definition: 'Prototype average yield increase estimate from reported monitoring records.' },
  { label: 'Soil Fertility Improved (Reports)', value: '5,642', change: '+15% vs Apr', icon: 'soil', tone: 'amber', definition: 'Prototype count of reports indicating improved soil fertility practices or outcomes.' },
  { label: 'tCO₂e Avoided (Cumulative)', value: '32,184', change: '+19% vs Apr', icon: 'co2', tone: 'teal', definition: 'Prototype cumulative climate-impact estimate. Not an official verified carbon accounting figure.' },
];

export const recentSubmissions: RecentSubmission[] = [
  { region: 'Morogoro Region', period: 'Loan & monitoring data — May 2025', status: 'Submitted', time: '2h ago' },
  { region: 'Mwanza Region', period: 'Loan & monitoring data — May 2025', status: 'Submitted', time: '4h ago' },
  { region: 'Kagera Region', period: 'Loan & monitoring data — May 2025', status: 'Submitted', time: '6h ago' },
];

export const programmeGoal = 'Increase the resilience of food-crop farmers to climate-change effects through accessible green financing, climate-smart technologies, sustainable agricultural practices, and capacity building.';
