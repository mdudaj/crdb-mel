export interface BeneficiaryRecord {
  id: string;
  name: string;
  category: 'Individual farmer' | 'Farmer group' | 'AMCOS' | 'SACCOS';
  region: string;
  district: string;
  borrowerStatus: 'Active borrower' | 'Training only' | 'Pending verification';
  loanType: 'Short-term' | 'Medium-term' | 'Long-term' | 'Not financed';
  technology: string;
  trained: boolean;
  verificationStatus: 'Verified' | 'Under review' | 'Incomplete';
  lastUpdated: string;
}

export const beneficiaryRecords: BeneficiaryRecord[] = [
  {
    id: 'BEN-MOR-001',
    name: 'Asha Mwakalinga',
    category: 'Individual farmer',
    region: 'Morogoro',
    district: 'Kilosa',
    borrowerStatus: 'Active borrower',
    loanType: 'Medium-term',
    technology: 'Solar-powered irrigation pumps',
    trained: true,
    verificationStatus: 'Verified',
    lastUpdated: 'May 31, 2025',
  },
  {
    id: 'BEN-MOR-002',
    name: 'Tujenge Farmers Group',
    category: 'Farmer group',
    region: 'Morogoro',
    district: 'Mvomero',
    borrowerStatus: 'Active borrower',
    loanType: 'Short-term',
    technology: 'Post-harvest technologies',
    trained: true,
    verificationStatus: 'Verified',
    lastUpdated: 'May 30, 2025',
  },
  {
    id: 'BEN-PWN-003',
    name: 'Kijani AMCOS',
    category: 'AMCOS',
    region: 'Pwani',
    district: 'Bagamoyo',
    borrowerStatus: 'Active borrower',
    loanType: 'Long-term',
    technology: 'Water harvesting and reservoirs',
    trained: false,
    verificationStatus: 'Under review',
    lastUpdated: 'May 29, 2025',
  },
  {
    id: 'BEN-DOD-004',
    name: 'Neema SACCOS',
    category: 'SACCOS',
    region: 'Dodoma',
    district: 'Chamwino',
    borrowerStatus: 'Pending verification',
    loanType: 'Not financed',
    technology: 'Drought-resistant seeds',
    trained: true,
    verificationStatus: 'Under review',
    lastUpdated: 'May 28, 2025',
  },
  {
    id: 'BEN-MWZ-005',
    name: 'Lake Zone Greenhouse Group',
    category: 'Farmer group',
    region: 'Mwanza',
    district: 'Ilemela',
    borrowerStatus: 'Active borrower',
    loanType: 'Medium-term',
    technology: 'Greenhouses',
    trained: true,
    verificationStatus: 'Verified',
    lastUpdated: 'May 27, 2025',
  },
  {
    id: 'BEN-KAG-006',
    name: 'Kagera Soil Health Cluster',
    category: 'Farmer group',
    region: 'Kagera',
    district: 'Bukoba Rural',
    borrowerStatus: 'Training only',
    loanType: 'Not financed',
    technology: 'Organic fertilizers',
    trained: true,
    verificationStatus: 'Incomplete',
    lastUpdated: 'May 24, 2025',
  },
  {
    id: 'BEN-ARU-007',
    name: 'Meru Hydroponics Cooperative',
    category: 'AMCOS',
    region: 'Arusha',
    district: 'Arumeru',
    borrowerStatus: 'Active borrower',
    loanType: 'Long-term',
    technology: 'Hydroponics',
    trained: false,
    verificationStatus: 'Verified',
    lastUpdated: 'May 22, 2025',
  },
  {
    id: 'BEN-MBE-008',
    name: 'Mbeya Climate Smart Farmers',
    category: 'Farmer group',
    region: 'Mbeya',
    district: 'Rungwe',
    borrowerStatus: 'Pending verification',
    loanType: 'Short-term',
    technology: 'Mixed cropping',
    trained: true,
    verificationStatus: 'Incomplete',
    lastUpdated: 'May 20, 2025',
  },
];
