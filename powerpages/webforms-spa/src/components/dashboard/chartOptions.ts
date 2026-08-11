import type { BarSeriesOption, LineSeriesOption, MapSeriesOption, PieSeriesOption } from 'echarts/charts';
import type {
  GridComponentOption,
  LegendComponentOption,
  TitleComponentOption,
  TooltipComponentOption,
  VisualMapComponentOption,
} from 'echarts/components';
import type { ComposeOption } from 'echarts/core';
import type { TrendPoint } from '../../prototype/tacatdpDashboardData';

export type DashboardChartOption = ComposeOption<
  | BarSeriesOption
  | LineSeriesOption
  | MapSeriesOption
  | PieSeriesOption
  | GridComponentOption
  | LegendComponentOption
  | TitleComponentOption
  | TooltipComponentOption
  | VisualMapComponentOption
>;

export const DISBURSEMENT_TREND_GRID_LEFT = 64;
export const DISBURSEMENT_TREND_POINT_LABEL_DISTANCE = 12;

export function buildDisbursementTrendOption(disbursementTrend: TrendPoint[]): DashboardChartOption {
  return {
    tooltip: { trigger: 'axis', valueFormatter: (value) => `TZS ${value}B` },
    grid: {
      left: DISBURSEMENT_TREND_GRID_LEFT,
      right: 24,
      top: 28,
      bottom: 30,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: disbursementTrend.map((point) => point.month),
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      name: 'TZS, billions',
      nameLocation: 'end',
      nameGap: 12,
      nameTextStyle: {
        color: '#64706A',
        fontSize: 11,
        fontWeight: 600,
      },
      axisLabel: {
        formatter: '{value}',
        margin: 12,
      },
      splitLine: { lineStyle: { color: '#E3E8E5' } },
    },
    series: [{
      type: 'line',
      smooth: true,
      symbolSize: 8,
      data: disbursementTrend.map((point) => point.value),
      label: {
        show: true,
        position: 'top',
        distance: DISBURSEMENT_TREND_POINT_LABEL_DISTANCE,
        formatter: ({ dataIndex }) => disbursementTrend[dataIndex].label,
        color: '#064E3B',
      },
      labelLayout: {
        hideOverlap: true,
      },
      lineStyle: { color: '#15803D', width: 3 },
      itemStyle: { color: '#15803D' },
      areaStyle: { color: 'rgba(21, 128, 61, 0.14)' },
    }],
  };
}
