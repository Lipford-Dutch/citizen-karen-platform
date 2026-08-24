export type AgencyCategory =
  | "Consumer"
  | "Civil rights"
  | "Safety"
  | "Health"
  | "Government"
  | "Environment";

export type AgencyDestination = {
  slug: string;
  title: string;
  agency: string;
  category: AgencyCategory;
  description: string;
  officialUrl: string;
  keywords: string[];
  direct?: boolean;
};

// Curated from Complaint_URLs_fixed.xlsx and API and URL research in this repo.
export const agencies: AgencyDestination[] = [
  {
    slug: "fcc",
    title: "FCC complaints",
    agency: "Federal Communications Commission",
    category: "Consumer",
    description: "Phone, internet, TV, radio, billing, and unwanted-call issues.",
    officialUrl: "https://consumercomplaints.fcc.gov/hc/en-us",
    keywords: ["robocall", "calls", "texts", "phone", "internet", "tv", "billing"],
    direct: true,
  },
  {
    slug: "cfpb",
    title: "Consumer finance",
    agency: "Consumer Financial Protection Bureau",
    category: "Consumer",
    description: "Banks, lenders, credit reports, debt collectors, and financial products.",
    officialUrl: "https://www.consumerfinance.gov/complaint/",
    keywords: ["bank", "credit", "loan", "mortgage", "debt", "collector", "finance"],
  },
  {
    slug: "doj-civil-rights",
    title: "Civil rights",
    agency: "Department of Justice",
    category: "Civil rights",
    description: "Discrimination, voting, housing, public accommodations, and hate incidents.",
    officialUrl: "https://civilrights.justice.gov/report/",
    keywords: ["discrimination", "voting", "housing", "hate", "rights", "bias"],
  },
  {
    slug: "osha",
    title: "Workplace safety",
    agency: "Occupational Safety and Health Administration",
    category: "Safety",
    description: "Unsafe working conditions, hazards, or workplace safety retaliation.",
    officialUrl: "https://www.osha.gov/workers/file-complaint",
    keywords: ["unsafe", "work", "workplace", "hazard", "retaliation", "osha"],
  },
  {
    slug: "epa",
    title: "Environmental concerns",
    agency: "Environmental Protection Agency",
    category: "Environment",
    description: "Pollution, illegal dumping, and hazards affecting air, water, or land.",
    officialUrl: "https://www.epa.gov/tips",
    keywords: ["pollution", "dumping", "water", "air", "land", "environment"],
  },
  {
    slug: "ftc",
    title: "Fraud & identity theft",
    agency: "Federal Trade Commission",
    category: "Consumer",
    description: "Scams, identity theft, online privacy, and unfair business practices.",
    officialUrl: "https://reportfraud.ftc.gov/assistant",
    keywords: ["fraud", "scam", "identity", "privacy", "online", "security"],
  },
  {
    slug: "usps",
    title: "Postal service",
    agency: "United States Postal Service",
    category: "Consumer",
    description: "Mail delivery, lost packages, and postal service problems.",
    officialUrl: "https://www.usps.com/help/contact-us.htm",
    keywords: ["mail", "package", "delivery", "postal", "usps"],
  },
  {
    slug: "eeoc",
    title: "Employment discrimination",
    agency: "Equal Employment Opportunity Commission",
    category: "Civil rights",
    description: "Workplace discrimination based on protected characteristics.",
    officialUrl: "https://www.eeoc.gov/filing-charge-discrimination",
    keywords: ["employment", "discrimination", "job", "race", "religion", "sex", "age", "disability"],
  },
  {
    slug: "cpsc",
    title: "Product safety",
    agency: "Consumer Product Safety Commission",
    category: "Safety",
    description: "Unsafe consumer products, toys, appliances, and household items.",
    officialUrl: "https://www.saferproducts.gov/IncidentReporting",
    keywords: ["product", "toy", "appliance", "unsafe", "injury", "recall"],
  },
  {
    slug: "dot-airline",
    title: "Airline service",
    agency: "Department of Transportation",
    category: "Consumer",
    description: "Air travel delays, cancellations, refunds, and accommodations.",
    officialUrl: "https://secure.dot.gov/air-travel-complaint",
    keywords: ["airline", "flight", "delay", "cancel", "refund", "travel"],
  },
  {
    slug: "nhtsa",
    title: "Vehicle safety",
    agency: "National Highway Traffic Safety Administration",
    category: "Safety",
    description: "Safety defects involving vehicles, tires, car seats, or equipment.",
    officialUrl: "https://www.nhtsa.gov/report-a-safety-problem",
    keywords: ["car", "vehicle", "tire", "defect", "safety", "equipment"],
  },
  {
    slug: "fda-food",
    title: "Food safety",
    agency: "Food and Drug Administration",
    category: "Health",
    description: "Contaminated, adulterated, or mislabeled food products.",
    officialUrl: "https://www.accessdata.fda.gov/scripts/medwatch/index.cfm?action=reporting.home",
    keywords: ["food", "contamination", "label", "illness", "fda"],
  },
  {
    slug: "fda-medwatch",
    title: "Drug or medical device safety",
    agency: "Food and Drug Administration",
    category: "Health",
    description: "Adverse events involving drugs, medical devices, or cosmetics.",
    officialUrl: "https://www.fda.gov/safety/medwatch-fda-safety-information-and-adverse-event-reporting-program",
    keywords: ["drug", "medicine", "device", "adverse", "cosmetic", "fda"],
  },
  {
    slug: "oversight",
    title: "Fraud, waste, or abuse",
    agency: "Council of the Inspectors General on Integrity and Efficiency",
    category: "Government",
    description: "Find the right Inspector General for federal fraud, waste, or abuse.",
    officialUrl: "https://www.oversight.gov/where-report-fraud-waste-abuse-or-retaliation",
    keywords: ["government", "misconduct", "waste", "abuse", "inspector general", "oig"],
  },
  {
    slug: "osc",
    title: "Whistleblower retaliation",
    agency: "Office of Special Counsel",
    category: "Government",
    description: "Prohibited personnel practices or whistleblower reprisal in federal employment.",
    officialUrl: "https://osc.gov/Services/Pages/DU-FileClaim.aspx",
    keywords: ["whistleblower", "retaliation", "federal employee", "personnel"],
  },
  {
    slug: "hhs-ocr",
    title: "Health civil rights & privacy",
    agency: "HHS Office for Civil Rights",
    category: "Civil rights",
    description: "Healthcare discrimination, human-services rights, or HIPAA privacy.",
    officialUrl: "https://www.hhs.gov/ocr/complaints/index.html",
    keywords: ["healthcare", "hipaa", "privacy", "discrimination", "hhs"],
  },
  {
    slug: "hud",
    title: "Housing discrimination",
    agency: "Department of Housing and Urban Development",
    category: "Civil rights",
    description: "Fair-housing issues involving rental, sales, lending, or accessibility.",
    officialUrl: "https://www.hud.gov/program_offices/fair_housing_equal_opp/online-complaint",
    keywords: ["housing", "rent", "landlord", "discrimination", "fair housing", "hud"],
  },
  {
    slug: "sec",
    title: "Securities fraud",
    agency: "Securities and Exchange Commission",
    category: "Consumer",
    description: "Investment fraud, broker misconduct, insider trading, and market abuse.",
    officialUrl: "https://www.sec.gov/complaint/tipscomplaint.shtml",
    keywords: ["investment", "broker", "stock", "securities", "fraud", "sec"],
  },
  {
    slug: "dol",
    title: "Wage & hour violations",
    agency: "Department of Labor",
    category: "Civil rights",
    description: "Unpaid wages, overtime, minimum wage, and child-labor concerns.",
    officialUrl: "https://www.dol.gov/agencies/whd/contact/complaints",
    keywords: ["wage", "pay", "overtime", "minimum wage", "labor"],
  },
  {
    slug: "bop",
    title: "Federal prison conditions",
    agency: "Federal Bureau of Prisons",
    category: "Government",
    description: "Inmate treatment, medical care, or federal facility conditions.",
    officialUrl: "https://www.bop.gov/inmates/concerns.jsp",
    keywords: ["prison", "inmate", "medical", "facility", "bop"],
  },
  {
    slug: "cms",
    title: "Medicare or Medicaid fraud",
    agency: "Centers for Medicare & Medicaid Services",
    category: "Health",
    description: "Suspected fraud, waste, or abuse involving Medicare or Medicaid.",
    officialUrl: "https://smpresource.org/you-can-help/report-fraud/",
    keywords: ["medicare", "medicaid", "health", "fraud", "cms"],
  },
  {
    slug: "ada",
    title: "Disability rights",
    agency: "Department of Justice ADA Information Line",
    category: "Civil rights",
    description: "Accessibility barriers in public services, employment, or transportation.",
    officialUrl: "https://www.ada.gov/file-a-complaint/",
    keywords: ["disability", "accessibility", "ada", "barrier", "accommodation"],
  },
  {
    slug: "voting",
    title: "Voting rights",
    agency: "Department of Justice Voting Section",
    category: "Civil rights",
    description: "Voter intimidation, ballot access, and voting-rights concerns.",
    officialUrl: "https://www.justice.gov/crt/voting-section",
    keywords: ["vote", "election", "ballot", "intimidation", "voting rights"],
  },
  {
    slug: "safe-helpline",
    title: "Military sexual assault support",
    agency: "Department of Defense Safe Helpline",
    category: "Safety",
    description: "Confidential support and reporting options for the military community.",
    officialUrl: "https://safehelpline.org/",
    keywords: ["military", "sexual assault", "harassment", "dod", "support"],
  },
  {
    slug: "eeoc-federal",
    title: "Federal employee EEO",
    agency: "Equal Employment Opportunity Commission",
    category: "Civil rights",
    description: "The EEO complaint process for employees of federal agencies.",
    officialUrl: "https://www.eeoc.gov/federal-sector/overview-federal-sector-eeo-complaint-process",
    keywords: ["federal employee", "eeo", "discrimination", "agency"],
  },
  {
    slug: "ice",
    title: "Immigration detention concerns",
    agency: "Immigration and Customs Enforcement",
    category: "Government",
    description: "Abuse, poor conditions, or rights concerns in immigration facilities.",
    officialUrl: "https://www.ice.gov/webform/ice-tip-form",
    keywords: ["immigration", "detention", "facility", "abuse", "ice"],
  },
  {
    slug: "fra",
    title: "Railroad safety",
    agency: "Federal Railroad Administration",
    category: "Safety",
    description: "Rail accidents, track defects, or hazardous-material transport.",
    officialUrl: "https://railroads.dot.gov/railroad-safety/federal-railroad-administration-alleged-violation-reporting-form",
    keywords: ["rail", "train", "track", "accident", "hazard", "fra"],
  },
  {
    slug: "fmcsa",
    title: "Commercial vehicle safety",
    agency: "Federal Motor Carrier Safety Administration",
    category: "Safety",
    description: "Unsafe trucking, buses, moving companies, or hazardous transport.",
    officialUrl: "https://nccdb.fmcsa.dot.gov/nccdb/",
    keywords: ["truck", "bus", "moving", "commercial vehicle", "highway", "fmcsa"],
  },
];

export function searchAgencies(query: string): AgencyDestination[] {
  const terms = query
    .toLocaleLowerCase()
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (!terms.length) return agencies;

  return agencies.filter((agency) => {
    const haystack = [
      agency.title,
      agency.agency,
      agency.category,
      agency.description,
      ...agency.keywords,
    ]
      .join(" ")
      .toLocaleLowerCase();
    return terms.every((term) => haystack.includes(term));
  });
}
