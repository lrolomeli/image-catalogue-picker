/**
 * Download catalog image candidates for a single product.
 * 
 * Usage (standalone):
 *   node download-images.js <productNum> <productName> <outputDir>
 * 
 * Usage (via server):
 *   POST /api/download with JSON body
 * 
 * Environment variables (.env):
 *   PEXELS_API_KEY
 *   UNSPLASH_ACCESS_KEY
 *   SERPER_API_KEY
 */

import dotenv from "dotenv";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const sharp = require("sharp");

const _filename = fileURLToPath(import.meta.url);
const _dirname = path.dirname(_filename);

dotenv.config({ path: path.join(_dirname, "../.env") });

// ─── Helpers ────────────────────────────────────────────────────────────────

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function nameToSlug(name) {
  return name
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, "")
    .trim()
    .replace(/\s+/g, "-");
}

function pad(n, len = 2) {
  return String(n).padStart(len, "0");
}

async function fetchJson(url, options) {
  try {
    const res = await fetch(url, options);
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

// ─── Image Sources ───────────────────────────────────────────────────────────

async function searchPexels(query) {
  const key = process.env.PEXELS_API_KEY;
  if (!key) return [];
  const data = await fetchJson(
    `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=3&orientation=square`,
    { headers: { Authorization: key } }
  );
  return data?.photos?.map(p => p.src?.large || p.src?.original).filter(Boolean) || [];
}

async function searchUnsplash(query) {
  const key = process.env.UNSPLASH_ACCESS_KEY;
  if (!key) return [];
  const data = await fetchJson(
    `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&per_page=3&orientation=squarish`,
    { headers: { Authorization: `Client-ID ${key}` } }
  );
  return data?.results?.map(r => r.urls?.regular).filter(Boolean) || [];
}

async function searchSerper(query) {
  const key = process.env.SERPER_API_KEY;
  if (!key) return [];
  const data = await fetchJson("https://google.serper.dev/images", {
    method: "POST",
    headers: { "X-API-KEY": key, "Content-Type": "application/json" },
    body: JSON.stringify({ q: query + " producto", num: 3 }),
  });
  return data?.images?.map(i => i.imageUrl).filter(Boolean) || [];
}

// ─── Download Image ──────────────────────────────────────────────────────────

async function downloadImage(url, outputPath) {
  try {
    const res = await fetch(url);
    if (!res.ok) return false;
    const buffer = Buffer.from(await res.arrayBuffer());
    if (buffer.length < 1000) return false;
    
    await sharp(buffer)
      .resize(800, 800, { fit: "inside", withoutEnlargement: true })
      .webp({ quality: 80 })
      .toFile(outputPath);
    return true;
  } catch (err) {
    console.error(`Download error: ${err.message}`);
    return false;
  }
}

// ─── Main Download Function ──────────────────────────────────────────────────

export async function downloadProductImages({ productNum, productName, outputDir }) {
  const slug = nameToSlug(productName);
  const folderName = `${pad(productNum)}-${slug}`;
  const candidateDir = path.join(outputDir, "_candidates", folderName);

  // Create directory
  if (!fs.existsSync(candidateDir)) {
    fs.mkdirSync(candidateDir, { recursive: true });
  }

  // Count existing
  const existing = fs.readdirSync(candidateDir).filter(f => f.endsWith(".webp")).length;
  if (existing >= 18) {
    return { success: true, count: existing, message: "Already has 18 candidates" };
  }

  console.log(`[${new Date().toISOString().slice(11, 19)}] Downloading for "${productName}"...`);

  // Collect URLs from all sources
  const jobs = [
    { name: "pexels", fn: () => searchPexels(productName) },
    { name: "unsplash-es", fn: () => searchUnsplash(productName) },
    { name: "unsplash-en", fn: () => searchUnsplash(productName + " food") },
    { name: "serper", fn: () => searchSerper(productName) },
  ];

  const results = await Promise.all(jobs.map(j => j.fn().catch(() => [])));
  const urls = [];
  for (const urlsArr of results) {
    urls.push(...urlsArr);
  }

  if (urls.length === 0) {
    return { success: false, error: "No image sources available", count: existing };
  }

  // Download up to 18
  let downloaded = 0;
  let bestPath = null;
  const toDownload = Math.min(urls.length, 18 - existing);

  for (let j = 0; j < toDownload; j++) {
    const idx = existing + j + 1;
    const imgPath = path.join(candidateDir, `${pad(idx)}.webp`);
    
    if (fs.existsSync(imgPath)) {
      downloaded++;
      continue;
    }

    const ok = await downloadImage(urls[j], imgPath);
    if (ok) {
      downloaded++;
      if (!bestPath) bestPath = imgPath;
    }
    await delay(250);
  }

  const totalNow = existing + downloaded;
  console.log(`[${new Date().toISOString().slice(11, 19)}] ✓ "${productName}": ${downloaded} new images (total: ${totalNow})`);

  return { success: true, count: totalNow, downloaded };
}

// ─── CLI Entry Point ─────────────────────────────────────────────────────────

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [, , productNum, productName, outputDir] = process.argv;
  
  if (!productNum || !productName || !outputDir) {
    console.error("Usage: node download-images.js <productNum> <productName> <outputDir>");
    process.exit(1);
  }

  const result = await downloadProductImages({
    productNum: parseInt(productNum),
    productName,
    outputDir,
  });

  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
}
