export interface BeneficiaryRecord {
  id: string;
  name: string;
  category: 'Individual farmer' | 'Farmer group' | 'AMCOS' | 'SACCOS';
  region: string;
  district: string;
  borrowerStatus: 'Active borrower' | 'Training only' | 'Pending verification';
  loanType: 'Short-term' | 'Medium-term' | 'Long-term' | 'Not financed';
  technology: string;
  projectParticipation: {
    programme: string;
    project: string;
    implementationPartner: string;
    enrolmentDate: string;
    participationRole: string;
  };
  finance: {
    loanAccountRef: string;
    disbursedAmount: string;
    outstandingBalance: string;
    repaymentRate: string;
  };
  technologiesFinanced: Array<{
    name: string;
    category: string;
    adoptionStage: 'Planned' | 'In use' | 'Scaling';
  }>;
  trainingSummary: {
    sessionsAttended: number;
    lastTopic: string;
    completionRate: string;
    lastTrainingDate: string;
  };
  latestSubmission: {
    form: string;
    reportingPeriod: string;
    status: 'Submitted' | 'Under review' | 'Returned' | 'Awaiting submission';
    completeness: string;
    dataSource: string;
  };
  identityGovernance?: {
    matchState: 'Linked to tracked entity' | 'Candidate match review' | 'Create new tracked entity' | 'Needs investigation';
    matchSignals: string;
    reviewerDecision: string;
  };
  groupMembership?: {
    membershipType: 'Individual beneficiary' | 'Group beneficiary' | 'AMCOS beneficiary' | 'SACCOS beneficiary';
    membersLinked: string;
    membershipStatus: 'Active' | 'Pending verification' | 'Not modelled';
  };
  locationHistory?: {
    currentLocation: string;
    source: string;
    effectiveFrom: string;
    historyState: 'Current profile location' | 'Correction pending' | 'Awaiting submission';
  };
  outcomeSnapshot: {
    areaUnderImprovedPractices: string;
    yieldIncrease: string;
    climateEstimate: string;
  };
  futureDataverseMapping: {
    table: string;
    recordId: string;
    relationshipNotes: string;
  };
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Climate-smart irrigation finance',
      implementationPartner: 'CRDB Sustainable Finance Unit',
      enrolmentDate: 'Jan 14, 2025',
      participationRole: 'Borrower and trained farmer',
    },
    finance: {
      loanAccountRef: 'Prototype loan LN-MOR-001',
      disbursedAmount: 'TZS 18.4M',
      outstandingBalance: 'TZS 11.2M',
      repaymentRate: '96%',
    },
    technologiesFinanced: [
      { name: 'Solar-powered irrigation pump', category: 'Water and irrigation', adoptionStage: 'In use' },
      { name: 'Drip irrigation kit', category: 'Water and irrigation', adoptionStage: 'Planned' },
    ],
    trainingSummary: {
      sessionsAttended: 3,
      lastTopic: 'Solar irrigation operation and maintenance',
      completionRate: '100%',
      lastTrainingDate: 'May 18, 2025',
    },
    latestSubmission: {
      form: 'Beneficiary baseline and monitoring',
      reportingPeriod: 'May 2025',
      status: 'Submitted',
      completeness: '98%',
      dataSource: 'Power Pages prototype form',
    },
    identityGovernance: {
      matchState: 'Linked to tracked entity',
      matchSignals: 'Project code, name, phone, village',
      reviewerDecision: 'Use existing mp_TrackedEntity after review',
    },
    groupMembership: {
      membershipType: 'Individual beneficiary',
      membersLinked: 'Not applicable',
      membershipStatus: 'Not modelled',
    },
    locationHistory: {
      currentLocation: 'Morogoro · Kilosa',
      source: 'Baseline submission',
      effectiveFrom: 'Jan 14, 2025',
      historyState: 'Current profile location',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: '3.2 ha',
      yieldIncrease: 'Estimated +24%',
      climateEstimate: 'Modelled tCO₂e avoided pending verification',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Future lookup from submissions, loans, trainings, and financed technologies.',
    },
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Post-harvest loss reduction',
      implementationPartner: 'District agricultural office',
      enrolmentDate: 'Feb 03, 2025',
      participationRole: 'Farmer group borrower',
    },
    finance: {
      loanAccountRef: 'Prototype loan LN-MOR-002',
      disbursedAmount: 'TZS 42.0M',
      outstandingBalance: 'TZS 26.8M',
      repaymentRate: '94%',
    },
    technologiesFinanced: [
      { name: 'Post-harvest storage equipment', category: 'Post-harvest', adoptionStage: 'In use' },
      { name: 'Warehouse handling tools', category: 'Post-harvest', adoptionStage: 'Scaling' },
    ],
    trainingSummary: {
      sessionsAttended: 2,
      lastTopic: 'Post-harvest handling and quality control',
      completionRate: '86%',
      lastTrainingDate: 'May 12, 2025',
    },
    latestSubmission: {
      form: 'Loan and monitoring data',
      reportingPeriod: 'May 2025',
      status: 'Submitted',
      completeness: '95%',
      dataSource: 'Power Pages prototype form',
    },
    identityGovernance: {
      matchState: 'Linked to tracked entity',
      matchSignals: 'Group name, district, programme enrolment',
      reviewerDecision: 'Treat group as beneficiary entity',
    },
    groupMembership: {
      membershipType: 'Group beneficiary',
      membersLinked: '32 member farmers planned for later linkage',
      membershipStatus: 'Active',
    },
    locationHistory: {
      currentLocation: 'Morogoro · Mvomero',
      source: 'Loan and monitoring submission',
      effectiveFrom: 'Feb 03, 2025',
      historyState: 'Current profile location',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: 'Group-reported 18.6 ha',
      yieldIncrease: 'Awaiting harvest report',
      climateEstimate: 'Not yet modelled',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Group entity should link to member farmers and submission history.',
    },
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Water harvesting infrastructure',
      implementationPartner: 'Regional implementation partner',
      enrolmentDate: 'Mar 08, 2025',
      participationRole: 'AMCOS borrower',
    },
    finance: {
      loanAccountRef: 'Prototype loan LN-PWN-003',
      disbursedAmount: 'TZS 85.5M',
      outstandingBalance: 'TZS 78.9M',
      repaymentRate: '89%',
    },
    technologiesFinanced: [
      { name: 'Water harvesting reservoir', category: 'Water and irrigation', adoptionStage: 'Planned' },
      { name: 'Improved irrigation channels', category: 'Water and irrigation', adoptionStage: 'Planned' },
    ],
    trainingSummary: {
      sessionsAttended: 1,
      lastTopic: 'Water-use governance for farmer organizations',
      completionRate: '54%',
      lastTrainingDate: 'Apr 24, 2025',
    },
    latestSubmission: {
      form: 'Beneficiary baseline and monitoring',
      reportingPeriod: 'May 2025',
      status: 'Under review',
      completeness: '82%',
      dataSource: 'Power Pages prototype form',
    },
    identityGovernance: {
      matchState: 'Candidate match review',
      matchSignals: 'Organization name and district match existing cooperative',
      reviewerDecision: 'Pending MEL officer confirmation',
    },
    groupMembership: {
      membershipType: 'AMCOS beneficiary',
      membersLinked: 'Member-level records not yet imported',
      membershipStatus: 'Pending verification',
    },
    locationHistory: {
      currentLocation: 'Pwani · Bagamoyo',
      source: 'Baseline submission',
      effectiveFrom: 'Mar 08, 2025',
      historyState: 'Correction pending',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: 'Implementation not complete',
      yieldIncrease: 'Baseline only',
      climateEstimate: 'Awaiting verification',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Organization entity should link to infrastructure asset records.',
    },
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Climate-smart input awareness',
      implementationPartner: 'Branch MEL focal person',
      enrolmentDate: 'Apr 02, 2025',
      participationRole: 'Pending borrower verification',
    },
    finance: {
      loanAccountRef: 'Not yet assigned',
      disbursedAmount: 'Not yet disbursed',
      outstandingBalance: 'Not applicable',
      repaymentRate: 'Not applicable',
    },
    technologiesFinanced: [
      { name: 'Drought-resistant seeds', category: 'Climate-smart inputs', adoptionStage: 'Planned' },
    ],
    trainingSummary: {
      sessionsAttended: 2,
      lastTopic: 'Drought-resilient crop selection',
      completionRate: '76%',
      lastTrainingDate: 'May 09, 2025',
    },
    latestSubmission: {
      form: 'Beneficiary baseline and monitoring',
      reportingPeriod: 'May 2025',
      status: 'Under review',
      completeness: '69%',
      dataSource: 'Power Pages prototype form',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: 'Not yet verified',
      yieldIncrease: 'Baseline only',
      climateEstimate: 'Not yet modelled',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Pending record should remain visible for data-quality follow-up.',
    },
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Protected cultivation finance',
      implementationPartner: 'CRDB branch and extension partner',
      enrolmentDate: 'Feb 17, 2025',
      participationRole: 'Farmer group borrower',
    },
    finance: {
      loanAccountRef: 'Prototype loan LN-MWZ-005',
      disbursedAmount: 'TZS 64.8M',
      outstandingBalance: 'TZS 41.5M',
      repaymentRate: '92%',
    },
    technologiesFinanced: [
      { name: 'Greenhouse structure', category: 'Protected cultivation', adoptionStage: 'In use' },
      { name: 'Mulching materials', category: 'Soil and moisture management', adoptionStage: 'In use' },
    ],
    trainingSummary: {
      sessionsAttended: 4,
      lastTopic: 'Greenhouse crop management',
      completionRate: '100%',
      lastTrainingDate: 'May 16, 2025',
    },
    latestSubmission: {
      form: 'Loan and monitoring data',
      reportingPeriod: 'May 2025',
      status: 'Submitted',
      completeness: '97%',
      dataSource: 'Power Pages prototype form',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: '2 greenhouse units',
      yieldIncrease: 'Estimated +31%',
      climateEstimate: 'Modelled estimate pending field verification',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Group entity should support crop-cycle and greenhouse-unit child records.',
    },
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Soil fertility improvement',
      implementationPartner: 'Training partner',
      enrolmentDate: 'Apr 19, 2025',
      participationRole: 'Training participant',
    },
    finance: {
      loanAccountRef: 'Not financed',
      disbursedAmount: 'Not yet disbursed',
      outstandingBalance: 'Not applicable',
      repaymentRate: 'Not applicable',
    },
    technologiesFinanced: [
      { name: 'Organic fertilizers', category: 'Soil health', adoptionStage: 'In use' },
      { name: 'Crop rotation', category: 'Sustainable practices', adoptionStage: 'Planned' },
    ],
    trainingSummary: {
      sessionsAttended: 2,
      lastTopic: 'Organic fertilizer application',
      completionRate: '64%',
      lastTrainingDate: 'May 05, 2025',
    },
    latestSubmission: {
      form: 'Beneficiary baseline and monitoring',
      reportingPeriod: 'May 2025',
      status: 'Returned',
      completeness: '58%',
      dataSource: 'Power Pages prototype form',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: 'Not yet complete',
      yieldIncrease: 'Not yet reported',
      climateEstimate: 'Awaiting submission correction',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Incomplete record should retain issue history and responsible organization.',
    },
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Water-efficient production finance',
      implementationPartner: 'Regional implementation partner',
      enrolmentDate: 'Mar 21, 2025',
      participationRole: 'AMCOS borrower',
    },
    finance: {
      loanAccountRef: 'Prototype loan LN-ARU-007',
      disbursedAmount: 'TZS 93.2M',
      outstandingBalance: 'TZS 88.1M',
      repaymentRate: '91%',
    },
    technologiesFinanced: [
      { name: 'Hydroponics kit', category: 'Water-efficient production', adoptionStage: 'Scaling' },
      { name: 'Water reservoir', category: 'Water and irrigation', adoptionStage: 'In use' },
    ],
    trainingSummary: {
      sessionsAttended: 1,
      lastTopic: 'Hydroponics system maintenance',
      completionRate: '48%',
      lastTrainingDate: 'Apr 29, 2025',
    },
    latestSubmission: {
      form: 'Loan and monitoring data',
      reportingPeriod: 'May 2025',
      status: 'Submitted',
      completeness: '90%',
      dataSource: 'Power Pages prototype form',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: 'Hydroponics pilot unit',
      yieldIncrease: 'Estimated +18%',
      climateEstimate: 'Modelled water-efficiency benefit',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Technology detail should link to financed equipment and outcome estimates.',
    },
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
    projectParticipation: {
      programme: 'TACATDP',
      project: 'Sustainable practices adoption',
      implementationPartner: 'Branch MEL focal person',
      enrolmentDate: 'Apr 27, 2025',
      participationRole: 'Pending verification group',
    },
    finance: {
      loanAccountRef: 'Prototype loan LN-MBE-008',
      disbursedAmount: 'TZS 21.7M',
      outstandingBalance: 'TZS 20.4M',
      repaymentRate: 'Awaiting first repayment',
    },
    technologiesFinanced: [
      { name: 'Mixed cropping', category: 'Sustainable practices', adoptionStage: 'Planned' },
      { name: 'Windbreak trees', category: 'Climate resilience', adoptionStage: 'Planned' },
    ],
    trainingSummary: {
      sessionsAttended: 2,
      lastTopic: 'Mixed cropping and farm planning',
      completionRate: '72%',
      lastTrainingDate: 'May 03, 2025',
    },
    latestSubmission: {
      form: 'Beneficiary baseline and monitoring',
      reportingPeriod: 'May 2025',
      status: 'Awaiting submission',
      completeness: 'Not yet submitted',
      dataSource: 'Power Pages prototype form',
    },
    outcomeSnapshot: {
      areaUnderImprovedPractices: 'Awaiting submission',
      yieldIncrease: 'Baseline not complete',
      climateEstimate: 'Not yet modelled',
    },
    futureDataverseMapping: {
      table: 'mp_TrackedEntity + beneficiary extension tables',
      recordId: 'Not yet mapped',
      relationshipNotes: 'Record needs submission follow-up before indicator reporting.',
    },
    trained: true,
    verificationStatus: 'Incomplete',
    lastUpdated: 'May 20, 2025',
  },
];
