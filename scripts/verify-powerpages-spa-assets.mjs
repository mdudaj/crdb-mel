#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(SCRIPT_DIR, '..');

const DEFAULT_DIST_ASSETS = join(REPO_ROOT, 'powerpages/webforms-spa/dist/assets');
const DEFAULT_WEB_FILES = join(
  REPO_ROOT,
  'powerpages/tacatdp-monitoring-tool-upload/tacatdp-monitoring-tool/web-files',
);

function usage() {
  return [
    'Usage: node scripts/verify-powerpages-spa-assets.mjs [options]',
    '',
    'Options:',
    '  --dist-assets <path>   Vite dist/assets directory.',
    '  --web-files <path>     Power Pages web-files directory to verify.',
    '  --fail-on-duplicates   Fail if more than one web-file record has the same adx_partialurl.',
    '  --json                 Emit a machine-readable JSON summary.',
    '  --help                 Show this help.',
    '',
    'Defaults:',
    `  --dist-assets ${DEFAULT_DIST_ASSETS}`,
    `  --web-files ${DEFAULT_WEB_FILES}`,
  ].join('\n');
}

function parseArgs(argv) {
  const options = {
    distAssets: DEFAULT_DIST_ASSETS,
    webFiles: DEFAULT_WEB_FILES,
    failOnDuplicates: false,
    json: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      console.log(usage());
      process.exit(0);
    }
    if (arg === '--fail-on-duplicates') {
      options.failOnDuplicates = true;
      continue;
    }
    if (arg === '--json') {
      options.json = true;
      continue;
    }
    if (arg === '--dist-assets') {
      const value = argv[index + 1];
      if (!value) throw new Error('--dist-assets requires a path');
      options.distAssets = resolve(value);
      index += 1;
      continue;
    }
    if (arg === '--web-files') {
      const value = argv[index + 1];
      if (!value) throw new Error('--web-files requires a path');
      options.webFiles = resolve(value);
      index += 1;
      continue;
    }
    throw new Error(`Unknown argument: ${arg}`);
  }

  return options;
}

function sha256(filePath) {
  return createHash('sha256').update(readFileSync(filePath)).digest('hex');
}

function yamlValue(text, key) {
  const line = text.split(/\r?\n/).find((entry) => entry.startsWith(`${key}: `));
  return line ? line.slice(key.length + 2).trim() : '';
}

function readWebFileRecords(webFiles) {
  return readdirSync(webFiles)
    .filter((file) => file.endsWith('.webfile.yml'))
    .map((metadata) => {
      const file = metadata.slice(0, -'.webfile.yml'.length);
      const text = readFileSync(join(webFiles, metadata), 'utf8');
      return {
        metadata,
        file,
        partialUrl: yamlValue(text, 'adx_partialurl'),
        filename: yamlValue(text, 'filename'),
      };
    });
}

function verify(options) {
  if (!existsSync(options.distAssets)) {
    throw new Error(`Missing Vite assets directory: ${options.distAssets}`);
  }
  if (!existsSync(options.webFiles)) {
    throw new Error(`Missing Power Pages web-files directory: ${options.webFiles}`);
  }

  const distFiles = readdirSync(options.distAssets)
    .filter((file) => !file.endsWith('.map'))
    .sort();
  const records = readWebFileRecords(options.webFiles);
  const missing = [];
  const mismatched = [];
  const duplicatePartialUrls = [];

  for (const asset of distFiles) {
    const candidates = records.filter((record) => record.partialUrl === asset);
    if (candidates.length === 0) {
      missing.push(asset);
      continue;
    }

    if (candidates.length > 1) {
      duplicatePartialUrls.push({
        partialUrl: asset,
        count: candidates.length,
        files: candidates.map((candidate) => candidate.file),
      });
    }

    const expectedHash = sha256(join(options.distAssets, asset));
    const hasMatchingBinary = candidates.some((candidate) => {
      const binary = join(options.webFiles, candidate.file);
      return existsSync(binary) && sha256(binary) === expectedHash;
    });

    if (!hasMatchingBinary) {
      mismatched.push(asset);
    }
  }

  return {
    distAssets: options.distAssets,
    webFiles: options.webFiles,
    assetCount: distFiles.length,
    missing,
    mismatched,
    duplicatePartialUrls,
  };
}

function printTextSummary(result, failOnDuplicates) {
  if (result.missing.length) {
    console.error(`Missing partial URLs:\n${result.missing.join('\n')}`);
  }
  if (result.mismatched.length) {
    console.error(`No matching binary for partial URLs:\n${result.mismatched.join('\n')}`);
  }
  if (result.duplicatePartialUrls.length) {
    const lines = result.duplicatePartialUrls.map((entry) => `${entry.partialUrl}: ${entry.count}`);
    const prefix = failOnDuplicates ? 'Duplicate partial URLs:' : 'Duplicate partial URLs observed:';
    console.error(`${prefix}\n${lines.join('\n')}`);
  }

  if (!result.missing.length && !result.mismatched.length && (!failOnDuplicates || !result.duplicatePartialUrls.length)) {
    console.log(
      `Power Pages SPA assets verified: ${result.assetCount} assets; duplicate partial URLs observed for ${result.duplicatePartialUrls.length} assets.`,
    );
  }
}

try {
  const options = parseArgs(process.argv.slice(2));
  const result = verify(options);
  if (options.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    printTextSummary(result, options.failOnDuplicates);
  }

  if (result.missing.length || result.mismatched.length || (options.failOnDuplicates && result.duplicatePartialUrls.length)) {
    process.exit(1);
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(2);
}
