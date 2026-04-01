/**
 * Fetches ALL Companies House data for Los Romeros Limited (06993349)
 * and saves to JSON files for report generation.
 */

const API_KEY = '4416608c-08ec-449e-8c5a-ddc66b5bb6b3';
const COMPANY_NUMBER = '06993349';
const BASE_URL = 'https://api.company-information.service.gov.uk';
const AUTH = 'Basic ' + Buffer.from(API_KEY + ':').toString('base64');

import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = join(__dirname, 'los_romeros_ch_data');
mkdirSync(OUTPUT_DIR, { recursive: true });

async function chFetch(path) {
  console.log(`Fetching: ${BASE_URL}${path}`);
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { Authorization: AUTH },
    signal: AbortSignal.timeout(30000)
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${path}`);
  return res.json();
}

function save(filename, data) {
  const filepath = join(OUTPUT_DIR, filename);
  writeFileSync(filepath, JSON.stringify(data, null, 2), 'utf8');
  console.log(`  Saved: ${filepath}`);
  return data;
}

async function getAllFilings() {
  let items = [];
  let startIndex = 0;
  const perPage = 100;
  while (true) {
    const data = await chFetch(
      `/company/${COMPANY_NUMBER}/filing-history?items_per_page=${perPage}&start_index=${startIndex}`
    );
    if (!data.items || data.items.length === 0) break;
    items = items.concat(data.items);
    console.log(`  Filings fetched so far: ${items.length} / ${data.total_count}`);
    if (items.length >= data.total_count) break;
    startIndex += perPage;
    await new Promise(r => setTimeout(r, 500));
  }
  return items;
}

async function getAllOfficers() {
  let items = [];
  let startIndex = 0;
  const perPage = 100;
  while (true) {
    const data = await chFetch(
      `/company/${COMPANY_NUMBER}/officers?items_per_page=${perPage}&start_index=${startIndex}`
    );
    if (!data.items || data.items.length === 0) break;
    items = items.concat(data.items);
    console.log(`  Officers fetched so far: ${items.length} / ${data.total_count}`);
    if (items.length >= data.total_count) break;
    startIndex += perPage;
    await new Promise(r => setTimeout(r, 500));
  }
  return items;
}

async function main() {
  console.log('=== Los Romeros Limited - Companies House Data Fetch ===\n');

  // 1. Company Profile
  console.log('1. Fetching company profile...');
  const company = await chFetch(`/company/${COMPANY_NUMBER}`);
  save('01_company_profile.json', company);

  await new Promise(r => setTimeout(r, 500));

  // 2. All Officers (current + resigned)
  console.log('\n2. Fetching all officers...');
  const officers = await getAllOfficers();
  save('02_officers_all.json', officers);

  await new Promise(r => setTimeout(r, 500));

  // 3. All Filings (paginated)
  console.log('\n3. Fetching complete filing history...');
  const filings = await getAllFilings();
  save('03_filings_all.json', filings);

  await new Promise(r => setTimeout(r, 500));

  // 4. PSC
  console.log('\n4. Fetching Persons with Significant Control...');
  const psc = await chFetch(`/company/${COMPANY_NUMBER}/persons-with-significant-control?items_per_page=100`);
  save('04_psc.json', psc);

  await new Promise(r => setTimeout(r, 500));

  // 5. PSC Statements
  console.log('\n5. Fetching PSC statements...');
  try {
    const pscStmt = await chFetch(`/company/${COMPANY_NUMBER}/persons-with-significant-control-statements?items_per_page=100`);
    save('05_psc_statements.json', pscStmt);
  } catch(e) { console.log('  No PSC statements: ' + e.message); }

  await new Promise(r => setTimeout(r, 500));

  // 6. Charges
  console.log('\n6. Fetching charges...');
  try {
    const charges = await chFetch(`/company/${COMPANY_NUMBER}/charges`);
    save('06_charges.json', charges);
  } catch(e) { console.log('  No charges: ' + e.message); }

  await new Promise(r => setTimeout(r, 500));

  // 7. UK Establishments
  console.log('\n7. Fetching registered office address history...');
  try {
    const regOffice = await chFetch(`/company/${COMPANY_NUMBER}/registered-office-address`);
    save('07_registered_office.json', regOffice);
  } catch(e) { console.log('  No office address history: ' + e.message); }

  await new Promise(r => setTimeout(r, 500));

  // 8. Exemptions
  console.log('\n8. Fetching exemptions...');
  try {
    const exemptions = await chFetch(`/company/${COMPANY_NUMBER}/exemptions`);
    save('08_exemptions.json', exemptions);
  } catch(e) { console.log('  No exemptions: ' + e.message); }

  // Summary
  console.log('\n=== FETCH COMPLETE ===');
  console.log(`Company: ${company.company_name}`);
  console.log(`Status: ${company.company_status}`);
  console.log(`Incorporated: ${company.date_of_creation}`);
  console.log(`Officers found: ${officers.length}`);
  console.log(`Filings found: ${filings.length}`);
  console.log(`PSC records: ${psc.total_results || 0}`);
  console.log(`\nAll data saved to: ${OUTPUT_DIR}`);

  // Print officer summary
  console.log('\n--- OFFICER SUMMARY ---');
  officers.forEach(o => {
    const resigned = o.resigned_on ? ` → RESIGNED ${o.resigned_on}` : ' [CURRENT]';
    console.log(`  ${o.officer_role.toUpperCase()}: ${o.name} | Appointed: ${o.appointed_on}${resigned}`);
  });

  // Print filing summary
  console.log('\n--- FILING SUMMARY (most recent first) ---');
  filings.forEach(f => {
    console.log(`  ${f.date} | ${f.type} | ${f.description}`);
  });
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
