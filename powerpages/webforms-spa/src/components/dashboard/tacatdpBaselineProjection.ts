import type { SubmissionReportRow } from '../../powerpages-api/types';
import type { NamedValue, RecentSubmission, RegionMetric, TrendPoint } from '../../prototype/tacatdpDashboardData';

export interface TacatdpBaselineProjection {
  rowsRead: number;
  rowsWithAnswers: number;
  finance: {
    reportedLoanAmountTzs: number;
    reportedLoanCount: number;
    rowsWithLoanAmount: number;
  };
  loanPortfolio: NamedValue[];
  regions: RegionMetric[];
  technologies: NamedValue[];
  disbursementTrend: TrendPoint[];
  recentSubmissions: RecentSubmission[];
  training: {
    records: number;
    farmersTrained: number;
    youthTrained: number;
  };
  area: {
    calculableRecords: number;
    validRecords: number;
    improvedHectares: number;
  };
  yield: {
    validDetailedRecords: number;
    validSimpleRecords: number;
    weightedDetailedChangePct: number | null;
    medianSimpleChangePct: number | null;
  };
  soil: {
    improvedReports: number;
  };
  water: {
    calculableRecords: number;
    validSavingRecords: number;
    savedCubicMeters: number;
    medianEfficiencyPct: number | null;
  };
  ghg: {
    calculableRecords: number;
    validSavingRecords: number;
    annualTco2eAvoided: number;
    lifetimeTco2eAvoided: number;
    negativeSavingRecords: number;
  };
  dataQualityFlags: number;
}

type RootAnswers = Record<string, unknown>;
type RegionAccumulator = {
  name: string;
  amountTzs: number;
  loans: number;
  profiles: number;
  farmersTrained: number;
  technologies: Map<string, number>;
  latestUpdate: string;
};
type CategoryAccumulator = {
  name: string;
  value: number;
  amountTzs: number;
};
type DashboardAggregate = {
  loans?: Array<{ amountTzs?: number; year?: string; stages?: string[] }>;
};

const ACRE_TO_HECTARE = 0.404686;
const DIESEL_KG_CO2E_PER_LITRE = 2.68;
const DASHBOARD_AGGREGATES_KEY = '__dashboardAggregates';
const LOAN_STAGE_ROOT_PREFIX = 'In which agricultural value chain stages did you invest your TACATDP loan(s)?/';
const TECHNOLOGY_PATTERNS: Array<{ name: string; pattern: RegExp }> = [
  { name: 'Climate-smart seeds', pattern: /TACATDP ARA Technology Deployed\/.+Climate-smart seeds|drought-resistant|drought tolerant/i },
  { name: 'Organic inputs', pattern: /TACATDP ARA Technology Deployed\/.+Organic inputs|organic fertilizer|bio-?fertili[sz]er|compost/i },
  { name: 'Efficient irrigation', pattern: /TACATDP ARA Technology Deployed\/.+Efficient irrigation|Newly Adopted Sustainable Irrigation Technology\/.+(drip|sprinkler|micro|precision)|Irrigation Type\/.+Solar-Powered Pump/i },
  { name: 'Rainwater harvesting/storage', pattern: /TACATDP ARA Technology Deployed\/.+Rainwater harvesting|Newly Adopted Sustainable Irrigation Technology\/.+(pond|reservoir|rainwater|storage)/i },
  { name: 'Irrigation infrastructure', pattern: /TACATDP ARA Technology Deployed\/.+Irrigation infrastructure|canal|paddy water management/i },
  { name: 'Greenhouses/protected farming', pattern: /TACATDP ARA Technology Deployed\/.+Greenhouses|greenhouse|protected farming|net shading/i },
  { name: 'Post-harvest/storage', pattern: /TACATDP ARA Technology Deployed\/.+(Harvesting and post-harvest|Storage systems|Drying technologies|Cold chain)/i },
  { name: 'Agro-processing/value addition', pattern: /TACATDP ARA Technology Deployed\/.+Agro-processing|New Financed Technology\/.+(processing|milling|oil extraction|dryer|cold room)/i },
  { name: 'Renewable energy', pattern: /TACATDP ARA Technology Deployed\/.+Renewable energy|New Financed Technology\/.+(Solar|Biogas|Biomass|Battery)/i },
  { name: 'Soil/water conservation', pattern: /TACATDP ARA Technology Deployed\/.+Soil and water conservation|mulching|minimum tillage|erosion control/i },
];

export function calculateTacatdpBaselineProjection(rows: SubmissionReportRow[]): TacatdpBaselineProjection {
  const projection: TacatdpBaselineProjection = {
    rowsRead: rows.length,
    rowsWithAnswers: 0,
    finance: {
      reportedLoanAmountTzs: 0,
      reportedLoanCount: 0,
      rowsWithLoanAmount: 0,
    },
    loanPortfolio: [],
    regions: [],
    technologies: [],
    disbursementTrend: [],
    recentSubmissions: [],
    training: {
      records: 0,
      farmersTrained: 0,
      youthTrained: 0,
    },
    area: {
      calculableRecords: 0,
      validRecords: 0,
      improvedHectares: 0,
    },
    yield: {
      validDetailedRecords: 0,
      validSimpleRecords: 0,
      weightedDetailedChangePct: null,
      medianSimpleChangePct: null,
    },
    soil: {
      improvedReports: 0,
    },
    water: {
      calculableRecords: 0,
      validSavingRecords: 0,
      savedCubicMeters: 0,
      medianEfficiencyPct: null,
    },
    ghg: {
      calculableRecords: 0,
      validSavingRecords: 0,
      annualTco2eAvoided: 0,
      lifetimeTco2eAvoided: 0,
      negativeSavingRecords: 0,
    },
    dataQualityFlags: 0,
  };

  const simpleYieldChanges: number[] = [];
  const waterEfficiencyValues: number[] = [];
  const loanStageAccumulators = new Map<string, CategoryAccumulator>();
  const regionAccumulators = new Map<string, RegionAccumulator>();
  const technologyAccumulators = new Map<string, CategoryAccumulator>();
  const trendAmountsByYear = new Map<string, number>();
  let detailedProductionBefore = 0;
  let detailedProductionAfter = 0;

  for (const row of rows) {
    const answers = parseRootAnswers(row.mp_rootanswersjson);
    if (Object.keys(answers).length === 0) continue;
    projection.rowsWithAnswers += 1;
    const aggregate = readDashboardAggregate(answers);
    const regionName = readText(answers, [/^Region$/i]) || 'Not recorded';
    const region = getRegionAccumulator(regionAccumulators, regionName);
    region.profiles += 1;
    region.latestUpdate = latestIso(region.latestUpdate, row.mp_updatedat || row.mp_projectedat || row.mp_submittedat || '');

    const rootLoanAmount = readNumber(answers, [/(?:^|\/)total_loan_amount$/i, /total.*loan.*amount/i]);
    const aggregateLoanAmount = sumAggregateLoanAmount(aggregate);
    const reportedLoanAmount = aggregateLoanAmount > 0 ? aggregateLoanAmount : rootLoanAmount ?? 0;
    if (reportedLoanAmount > 0) {
      projection.finance.reportedLoanAmountTzs += reportedLoanAmount;
      projection.finance.rowsWithLoanAmount += 1;
      region.amountTzs += reportedLoanAmount;
    }

    const rootLoanCount = readNumber(answers, [/Since joining TACATDP.*loans/i, /number.*loans/i]);
    const reportedLoanCount = aggregate.loans?.length || (rootLoanCount && rootLoanCount > 0 ? rootLoanCount : reportedLoanAmount > 0 ? 1 : 0);
    projection.finance.reportedLoanCount += reportedLoanCount;
    region.loans += reportedLoanCount;

    for (const loan of aggregate.loans ?? []) {
      if (loan.year && loan.amountTzs && loan.amountTzs > 0) {
        trendAmountsByYear.set(loan.year, (trendAmountsByYear.get(loan.year) ?? 0) + loan.amountTzs);
      }
    }

    const aggregateLoans = aggregate.loans ?? [];
    const loanStages = aggregateLoans.some((loan) => loan.stages?.length)
      ? aggregateLoans.flatMap((loan) => loan.stages ?? []).filter(Boolean)
      : readSelectedLoanStages(answers);
    const allocatedStageAmount = loanStages.length > 0 ? reportedLoanAmount / loanStages.length : 0;
    for (const stage of loanStages) {
      const category = getCategoryAccumulator(loanStageAccumulators, simplifyLoanStageName(stage));
      category.value += 1;
      category.amountTzs += allocatedStageAmount;
    }

    const farmersTrained = readNumber(answers, [
      /(?:^|\/)total_trained$/i,
      /total.*trained/i,
      /farmers?.*trained/i,
    ]);
    if (isUsableNumber(farmersTrained)) {
      projection.training.records += 1;
      projection.training.farmersTrained += farmersTrained;
      region.farmersTrained += farmersTrained;
    }

    const youthTrained = readNumber(answers, [
      /(?:^|\/)total_youth_trained$/i,
      /(?:^|\/)total_youth$/i,
      /youth.*trained/i,
    ]);
    if (isUsableNumber(youthTrained)) {
      projection.training.youthTrained += youthTrained;
    }

    const baselineAcres = readNumber(answers, [
      /(?:^|\/)land_baseline$/i,
      /before.*tacatdp.*loan/i,
      /baseline.*(acre|farm|land)/i,
    ]);
    const afterAcres = readNumber(answers, [
      /(?:^|\/)land_after$/i,
      /after.*tacatdp.*loan/i,
      /current.*(acre|farm|land)/i,
    ]);
    if (isUsableNumber(baselineAcres) && isUsableNumber(afterAcres)) {
      projection.area.calculableRecords += 1;
      const increaseAcres = afterAcres - baselineAcres;
      if (increaseAcres >= 0) {
        projection.area.validRecords += 1;
        projection.area.improvedHectares += increaseAcres * ACRE_TO_HECTARE;
      } else {
        projection.dataQualityFlags += 1;
      }
    }

    const farmSize = readNumber(answers, [/(?:^|\/)farm_size$/i, /farm.*size/i]);
    const productionBefore = readNumber(answers, [/(?:^|\/)production_before$/i, /production.*before/i]);
    const productionAfter = readNumber(answers, [/(?:^|\/)production_after$/i, /production.*after/i]);
    if (isPositiveNumber(farmSize) && isPositiveNumber(productionBefore) && isUsableNumber(productionAfter)) {
      projection.yield.validDetailedRecords += 1;
      detailedProductionBefore += productionBefore;
      detailedProductionAfter += productionAfter;
      if (productionAfter <= 0) {
        projection.dataQualityFlags += 1;
      }
    }

    const yieldBase = readNumber(answers, [/(?:^|\/)yield_base$/i, /yield.*base/i, /yield.*before/i]);
    const yieldAfter = readNumber(answers, [/(?:^|\/)yield_after1$/i, /(?:^|\/)yield_after2$/i, /yield.*after/i, /current.*yield/i]);
    if (isPositiveNumber(yieldBase) && isUsableNumber(yieldAfter)) {
      projection.yield.validSimpleRecords += 1;
      simpleYieldChanges.push(((yieldAfter - yieldBase) / yieldBase) * 100);
      if (yieldAfter <= 0) {
        projection.dataQualityFlags += 1;
      }
    }

    if (readTruthy(answers, [/soil.*fertility/i, /organic.*fertili[sz]er/i, /bio-?fertili[sz]er/i])) {
      projection.soil.improvedReports += 1;
    }

    const rowTechnologies = classifyTechnologies(answers);
    for (const technology of rowTechnologies) {
      const category = getCategoryAccumulator(technologyAccumulators, technology);
      category.value += 1;
      category.amountTzs += reportedLoanAmount;
      region.technologies.set(technology, (region.technologies.get(technology) ?? 0) + 1);
    }

    const waterBase = readNumber(answers, [/(?:^|\/)water_base$/i, /water.*baseline/i, /baseline.*water/i]);
    const waterAfter = readNumber(answers, [/(?:^|\/)water_after$/i, /water.*after/i, /current.*water/i]);
    if (isPositiveNumber(waterBase) && isUsableNumber(waterAfter)) {
      projection.water.calculableRecords += 1;
      const savedLitres = waterBase - waterAfter;
      if (savedLitres > 0) {
        projection.water.validSavingRecords += 1;
        projection.water.savedCubicMeters += savedLitres / 1000;
        waterEfficiencyValues.push((savedLitres / waterBase) * 100);
      } else {
        projection.dataQualityFlags += 1;
      }
    }

    const baselineHours = readNumber(answers, [/(?:^|\/)base_hours$/i, /baseline.*hours/i, /hours.*year/i]);
    const dieselRate = readNumber(answers, [/(?:^|\/)diesel_rate$/i, /diesel.*rate/i, /litres?.*hour/i]);
    const projectDiesel = readNumber(answers, [/(?:^|\/)diesel_proj$/i, /project.*diesel/i, /diesel.*after/i]);
    const lifespanYears = readNumber(answers, [/(?:^|\/)lifespan$/i, /lifespan/i]);
    if (isPositiveNumber(baselineHours) && isPositiveNumber(dieselRate) && isUsableNumber(projectDiesel)) {
      projection.ghg.calculableRecords += 1;
      const baselineDiesel = baselineHours * dieselRate;
      const annualTco2e = ((baselineDiesel - projectDiesel) * DIESEL_KG_CO2E_PER_LITRE) / 1000;
      if (annualTco2e > 0) {
        projection.ghg.validSavingRecords += 1;
        projection.ghg.annualTco2eAvoided += annualTco2e;
        projection.ghg.lifetimeTco2eAvoided += annualTco2e * (isPositiveNumber(lifespanYears) ? lifespanYears : 1);
      } else {
        projection.ghg.negativeSavingRecords += 1;
        projection.dataQualityFlags += 1;
      }
    }
  }

  if (detailedProductionBefore > 0) {
    projection.yield.weightedDetailedChangePct = ((detailedProductionAfter - detailedProductionBefore) / detailedProductionBefore) * 100;
  }
  projection.yield.medianSimpleChangePct = median(simpleYieldChanges);
  projection.water.medianEfficiencyPct = median(waterEfficiencyValues);
  projection.loanPortfolio = buildLoanPortfolioValues(loanStageAccumulators);
  projection.regions = buildRegions(regionAccumulators);
  projection.technologies = buildTechnologyValues(technologyAccumulators);
  projection.disbursementTrend = buildTrend(trendAmountsByYear);
  projection.recentSubmissions = buildRecentSubmissions(rows);

  return projection;
}

function parseRootAnswers(value?: string): RootAnswers {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value) as unknown;
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {};
    return parsed as RootAnswers;
  } catch {
    return {};
  }
}

function readNumber(answers: RootAnswers, patterns: RegExp[]): number | null {
  for (const [key, value] of Object.entries(answers)) {
    if (!patterns.some((pattern) => pattern.test(key))) continue;
    const numeric = toNumber(value);
    if (numeric !== null) return numeric;
  }
  return null;
}

function readText(answers: RootAnswers, patterns: RegExp[]): string {
  for (const [key, value] of Object.entries(answers)) {
    if (!patterns.some((pattern) => pattern.test(key))) continue;
    if (typeof value === 'string') return value.trim();
    if (typeof value === 'number') return String(value);
  }
  return '';
}

function readTruthy(answers: RootAnswers, patterns: RegExp[]): boolean {
  return Object.entries(answers).some(([key, value]) => patterns.some((pattern) => pattern.test(key)) && isTruthyAnswer(value));
}

function toNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value !== 'string') return null;
  const normalized = value.replace(/,/g, '').trim();
  if (!normalized) return null;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function isTruthyAnswer(value: unknown): boolean {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value !== 'string') return false;
  const normalized = value.trim().toLowerCase();
  return Boolean(normalized && !['0', 'false', 'no', 'n/a', 'none'].includes(normalized));
}

function readDashboardAggregate(answers: RootAnswers): DashboardAggregate {
  const value = answers[DASHBOARD_AGGREGATES_KEY];
  if (!value || typeof value !== 'object' || Array.isArray(value)) return {};
  return value as DashboardAggregate;
}

function sumAggregateLoanAmount(aggregate: DashboardAggregate) {
  return (aggregate.loans ?? []).reduce((total, loan) => total + (isUsableNumber(loan.amountTzs ?? null) ? loan.amountTzs ?? 0 : 0), 0);
}

function classifyTechnologies(answers: RootAnswers): string[] {
  return TECHNOLOGY_PATTERNS
    .filter(({ pattern }) => Object.entries(answers).some(([key, value]) => pattern.test(key) && isTruthyAnswer(value)))
    .map(({ name }) => name);
}

function readSelectedLoanStages(answers: RootAnswers): string[] {
  return Object.entries(answers)
    .filter(([key, value]) => key.startsWith(LOAN_STAGE_ROOT_PREFIX) && isTruthyAnswer(value))
    .map(([key]) => key.slice(LOAN_STAGE_ROOT_PREFIX.length))
    .filter(Boolean);
}

function simplifyLoanStageName(stage: string): string {
  return stage
    .replace(/^\s+|\s+$/g, '')
    .replace('Weeding / Field Management Stage', 'Field Management')
    .replace('Pre-harvest / Pest Control Stage', 'Pest Control')
    .replace('Storage / Warehousing Stage', 'Warehousing')
    .replace('Value Addition / Processing Stage', 'Processing')
    .replace('Marketing / Trading Stage', 'Trading')
    .replace(/\s+Stage$/i, '');
}

function getRegionAccumulator(regions: Map<string, RegionAccumulator>, name: string): RegionAccumulator {
  const normalizedName = name.trim() || 'Not recorded';
  const existing = regions.get(normalizedName);
  if (existing) return existing;
  const created: RegionAccumulator = {
    name: normalizedName,
    amountTzs: 0,
    loans: 0,
    profiles: 0,
    farmersTrained: 0,
    technologies: new Map<string, number>(),
    latestUpdate: '',
  };
  regions.set(normalizedName, created);
  return created;
}

function getCategoryAccumulator(categories: Map<string, CategoryAccumulator>, name: string): CategoryAccumulator {
  const existing = categories.get(name);
  if (existing) return existing;
  const created = { name, value: 0, amountTzs: 0 };
  categories.set(name, created);
  return created;
}

function buildRegions(regions: Map<string, RegionAccumulator>): RegionMetric[] {
  return [...regions.values()]
    .filter((region) => region.name !== 'Not recorded')
    .sort((left, right) => right.amountTzs - left.amountTzs || right.profiles - left.profiles)
    .map((region) => ({
      name: region.name,
      disbursed: toBillions(region.amountTzs),
      disbursedLabel: `TZS ${formatBillions(region.amountTzs)}B`,
      loans: Math.round(region.loans),
      borrowers: region.profiles,
      repaymentRate: 'Pending core banking',
      farmersTrained: Math.round(region.farmersTrained),
      technologies: [...region.technologies.entries()]
        .sort((left, right) => right[1] - left[1])
        .slice(0, 3)
        .map(([name]) => name),
      submissionCompleteness: 'Baseline imported',
    }));
}

function buildTechnologyValues(categories: Map<string, CategoryAccumulator>): NamedValue[] {
  const total = [...categories.values()].reduce((sum, item) => sum + item.value, 0);
  if (total === 0) return [];
  return [...categories.values()]
    .sort((left, right) => right.value - left.value)
    .slice(0, 6)
    .map((item) => ({
      name: item.name,
      value: item.value,
      percent: Math.round((item.value / total) * 100),
      amount: `TZS ${formatBillions(item.amountTzs)}B reported`,
    }));
}

function buildLoanPortfolioValues(categories: Map<string, CategoryAccumulator>): NamedValue[] {
  const total = [...categories.values()].reduce((sum, item) => sum + item.value, 0);
  if (total === 0) return [];
  return [...categories.values()]
    .sort((left, right) => right.value - left.value || right.amountTzs - left.amountTzs)
    .slice(0, 3)
    .map((item) => ({
      name: item.name,
      value: item.value,
      percent: Math.round((item.value / total) * 100),
      amount: `TZS ${formatBillions(item.amountTzs)}B allocated`,
    }));
}

function buildTrend(amountsByYear: Map<string, number>): TrendPoint[] {
  const entries = [...amountsByYear.entries()]
    .filter(([year, amount]) => /^\d{4}$/.test(year) && amount > 0)
    .sort(([left], [right]) => left.localeCompare(right));
  let cumulative = 0;
  return entries.map(([year, amount]) => {
    cumulative += amount;
    const value = toBillions(cumulative);
    return { month: year, value, label: `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })}B` };
  });
}

function buildRecentSubmissions(rows: SubmissionReportRow[]): RecentSubmission[] {
  return [...rows]
    .sort((left, right) => new Date(right.mp_updatedat || right.mp_projectedat || right.mp_submittedat || '').getTime() - new Date(left.mp_updatedat || left.mp_projectedat || left.mp_submittedat || '').getTime())
    .slice(0, 3)
    .map((row) => {
      const answers = parseRootAnswers(row.mp_rootanswersjson);
      const region = readText(answers, [/^Region$/i]) || 'Unknown';
      return {
        region: `${region} Region`,
        period: 'Baseline import projection',
        status: 'Submitted',
        time: formatRelativeDate(row.mp_updatedat || row.mp_projectedat || row.mp_submittedat || ''),
      };
    });
}

function latestIso(left: string, right: string) {
  if (!left) return right;
  if (!right) return left;
  return new Date(right).getTime() > new Date(left).getTime() ? right : left;
}

function toBillions(value: number) {
  return Number((value / 1_000_000_000).toFixed(3));
}

function formatBillions(value: number) {
  return toBillions(value).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

function formatRelativeDate(value: string) {
  if (!value) return 'Pending';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Updated';
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(date);
}

function isUsableNumber(value: number | null): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function isPositiveNumber(value: number | null): value is number {
  return isUsableNumber(value) && value > 0;
}

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) return sorted[middle];
  return (sorted[middle - 1] + sorted[middle]) / 2;
}
