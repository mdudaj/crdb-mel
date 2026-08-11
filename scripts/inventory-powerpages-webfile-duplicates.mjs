#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(SCRIPT_DIR, '..');

const DEFAULT_WEB_FILES = join(
  REPO_ROOT,
  'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files',
);
const DEFAULT_CANONICAL_WEB_FILES = join(
  REPO_ROOT,
  'powerpages/tacatdp-monitoring-tool/.powerpages-site/web-files',
);
const DEFAULT_DIST_ASSETS = join(REPO_ROOT, 'powerpages/webforms-spa/dist/assets');

function usage() {
  return [
    'Usage: node scripts/inventory-powerpages-webfile-duplicates.mjs [options]',
    '',
    'Options:',
    '  --web-files <path>             Downloaded Power Pages web-files directory.',
    '  --canonical-web-files <path>   Committed/canonical Power Pages web-files directory.',
    '  --dist-assets <path>           Vite dist/assets directory used for hash comparison.',
    '  --only <partialurl>            Report one duplicate partial URL.',
    '  --markdown                     Emit Markdown report.',
    '  --json                         Emit JSON report.',
    '  --help                         Show this help.',
    '',
    'Defaults:',
    `  --web-files ${DEFAULT_WEB_FILES}`,
    `  --canonical-web-files ${DEFAULT_CANONICAL_WEB_FILES}`,
    `  --dist-assets ${DEFAULT_DIST_ASSETS}`,
  ].join('\n');
}

function parseArgs(argv) {
  const options = {
    webFiles: DEFAULT_WEB_FILES,
    canonicalWebFiles: DEFAULT_CANONICAL_WEB_FILES,
    distAssets: DEFAULT_DIST_ASSETS,
    only: '',
    format: 'text',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      console.log(usage());
      process.exit(0);
    }
    if (arg === '--markdown') {
      options.format = 'markdown';
      continue;
    }
    if (arg === '--json') {
      options.format = 'json';
      continue;
    }
    if (arg === '--web-files' || arg === '--canonical-web-files' || arg === '--dist-assets' || arg === '--only') {
      const value = argv[index + 1];
      if (!value) throw new Error(`${arg} requires a value`);
      if (arg === '--web-files') options.webFiles = resolve(value);
      if (arg === '--canonical-web-files') options.canonicalWebFiles = resolve(value);
      if (arg === '--dist-assets') options.distAssets = resolve(value);
      if (arg === '--only') options.only = value;
      index += 1;
      continue;
    }
    throw new Error(`Unknown argument: ${arg}`);
  }

  return options;
}

function yamlValue(text, key) {
  const line = text.split(/\r?\n/).find((entry) => entry.startsWith(`${key}: `));
  return line ? line.slice(key.length + 2).trim() : '';
}

function sha256IfExists(path) {
  if (!existsSync(path)) return '';
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function readRecords(webFiles) {
  if (!existsSync(webFiles)) throw new Error(`Missing web-files directory: ${webFiles}`);
  return readdirSync(webFiles)
    .filter((file) => file.endsWith('.webfile.yml'))
    .map((metadata) => {
      const file = metadata.slice(0, -'.webfile.yml'.length);
      const metadataPath = join(webFiles, metadata);
      const binaryPath = join(webFiles, file);
      const text = readFileSync(metadataPath, 'utf8');
      return {
        metadata,
        file,
        partialUrl: yamlValue(text, 'adx_partialurl'),
        name: yamlValue(text, 'adx_name'),
        filename: yamlValue(text, 'filename'),
        webFileId: yamlValue(text, 'adx_webfileid'),
        annotationId: yamlValue(text, 'annotationid'),
        parentPageId: yamlValue(text, 'adx_parentpageid'),
        publishingStateId: yamlValue(text, 'adx_publishingstateid'),
        mimeType: yamlValue(text, 'mimetype'),
        binaryExists: existsSync(binaryPath),
        binarySha256: sha256IfExists(binaryPath),
      };
    });
}

function groupByPartial(records) {
  const groups = new Map();
  for (const record of records) {
    if (!record.partialUrl) continue;
    const bucket = groups.get(record.partialUrl) ?? [];
    bucket.push(record);
    groups.set(record.partialUrl, bucket);
  }
  return groups;
}

function buildReport(options) {
  const downloadedRecords = readRecords(options.webFiles);
  const canonicalRecords = readRecords(options.canonicalWebFiles);
  const downloadedGroups = groupByPartial(downloadedRecords);
  const canonicalGroups = groupByPartial(canonicalRecords);

  const duplicateGroups = Array.from(downloadedGroups.entries())
    .filter(([partialUrl, records]) => records.length > 1 && (!options.only || partialUrl === options.only))
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([partialUrl, records]) => {
      const canonicalMatches = canonicalGroups.get(partialUrl) ?? [];
      const distHash = sha256IfExists(join(options.distAssets, partialUrl));
      const downloadedDistMatches = distHash ? records.filter((record) => record.binarySha256 === distHash) : [];
      return {
        partialUrl,
        count: records.length,
        canonicalCount: canonicalMatches.length,
        distAssetExists: Boolean(distHash),
        distSha256: distHash,
        downloadedDistMatchCount: downloadedDistMatches.length,
        downloadedDistMatchFiles: downloadedDistMatches.map((record) => record.file),
        allDownloadedBinariesMatchDist: Boolean(distHash) && downloadedDistMatches.length === records.length,
        downloadedRecords: records,
        canonicalRecords: canonicalMatches,
      };
    });

  return {
    webFiles: options.webFiles,
    canonicalWebFiles: options.canonicalWebFiles,
    distAssets: options.distAssets,
    downloadedRecordCount: downloadedRecords.length,
    canonicalRecordCount: canonicalRecords.length,
    duplicatePartialUrlCount: duplicateGroups.length,
    duplicateGroups,
  };
}

function shortHash(hash) {
  return hash ? hash.slice(0, 12) : 'missing';
}

function printText(report) {
  console.log(`Downloaded records: ${report.downloadedRecordCount}`);
  console.log(`Canonical records: ${report.canonicalRecordCount}`);
  console.log(`Duplicate partial URLs: ${report.duplicatePartialUrlCount}`);
  for (const group of report.duplicateGroups) {
    console.log('');
    console.log(`${group.partialUrl}: ${group.count} downloaded records; canonical package has ${group.canonicalCount}`);
    console.log(`dist asset: ${group.distAssetExists ? 'present' : 'missing'}; downloaded records matching dist: ${group.downloadedDistMatchCount}`);
    for (const record of group.downloadedRecords) {
      console.log(`- ${record.file} webfile=${record.webFileId} annotation=${record.annotationId} sha=${shortHash(record.binarySha256)}`);
    }
  }
}

function markdownCell(value) {
  return String(value).replaceAll('|', '\\|');
}

function printMarkdown(report) {
  console.log('# Power Pages duplicate webfile inventory');
  console.log('');
  console.log(`- Downloaded web-files: \`${relative(REPO_ROOT, report.webFiles)}\``);
  console.log(`- Canonical web-files: \`${relative(REPO_ROOT, report.canonicalWebFiles)}\``);
  console.log(`- Vite assets: \`${relative(REPO_ROOT, report.distAssets)}\``);
  console.log(`- Downloaded records: ${report.downloadedRecordCount}`);
  console.log(`- Canonical records: ${report.canonicalRecordCount}`);
  console.log(`- Duplicate partial URLs: ${report.duplicatePartialUrlCount}`);
  console.log('');

  for (const group of report.duplicateGroups) {
    console.log(`## ${group.partialUrl}`);
    console.log('');
    console.log(`- Downloaded duplicate records: ${group.count}`);
    console.log(`- Canonical package records: ${group.canonicalCount}`);
    console.log(`- Dist asset exists: ${group.distAssetExists ? 'yes' : 'no'}`);
    console.log(`- Downloaded records matching dist hash: ${group.downloadedDistMatchCount}`);
    if (group.downloadedDistMatchFiles.length) {
      console.log(`- Dist-matching local files: ${group.downloadedDistMatchFiles.map((file) => `\`${file}\``).join(', ')}`);
    }
    console.log('');
    console.log('| Local file | Webfile ID | Annotation ID | Parent page ID | SHA-256 |');
    console.log('| --- | --- | --- | --- | --- |');
    for (const record of group.downloadedRecords) {
      console.log(`| ${markdownCell(record.file)} | ${record.webFileId} | ${record.annotationId} | ${record.parentPageId} | ${shortHash(record.binarySha256)} |`);
    }
    console.log('');
  }
}

try {
  const options = parseArgs(process.argv.slice(2));
  const report = buildReport(options);
  if (options.format === 'json') {
    console.log(JSON.stringify(report, null, 2));
  } else if (options.format === 'markdown') {
    printMarkdown(report);
  } else {
    printText(report);
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(2);
}
