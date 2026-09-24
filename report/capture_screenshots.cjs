const puppeteer = require('../frontend/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT_DIR = path.resolve(__dirname, 'explainer_images');

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function capture() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    defaultViewport: { width: 1440, height: 900 }
  });

  const page = await browser.newPage();
  console.log('Navigating to http://localhost:3000 ...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle2', timeout: 30000 });

  // Wait for initial simulation to load
  await sleep(4000);

  // 1. Capture Topology View (high-res fresh screenshot)
  await page.screenshot({ path: path.join(OUT_DIR, '01_topology_view.png') });
  console.log('Saved 01_topology_view.png');

  // 2. Click Playback tab
  console.log('Clicking Playback tab...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const tab = btns.find((b) => b.textContent && b.textContent.includes('Playback'));
    if (tab) tab.click();
  });
  await sleep(2500);

  // Scrub round slider to round 35
  await page.evaluate(() => {
    const slider = document.querySelector('input[type="range"]');
    if (slider) {
      slider.value = '35';
      slider.dispatchEvent(new Event('input', { bubbles: true }));
      slider.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await sleep(1500);
  await page.screenshot({ path: path.join(OUT_DIR, '02_playback_scrubber.png') });
  console.log('Saved 02_playback_scrubber.png');

  // 3. Click Heatmap tab
  console.log('Clicking Heatmap tab...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const tab = btns.find((b) => b.textContent && b.textContent.includes('Heatmap'));
    if (tab) tab.click();
  });
  await sleep(2500);
  await page.screenshot({ path: path.join(OUT_DIR, '03_energy_heatmap.png') });
  console.log('Saved 03_energy_heatmap.png');

  // 4. Click Analytics tab
  console.log('Clicking Analytics tab...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const tab = btns.find((b) => b.textContent && b.textContent.includes('Analytics'));
    if (tab) tab.click();
  });
  await sleep(3000);
  await page.screenshot({ path: path.join(OUT_DIR, '04_analytics_charts.png') });
  console.log('Saved 04_analytics_charts.png');

  // 5. Click Experiments tab & Shadow Occlusion sub-tab
  console.log('Clicking Experiments tab...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const tab = btns.find((b) => b.textContent && b.textContent.includes('Experiments'));
    if (tab) tab.click();
  });
  await sleep(1500);
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const sub = btns.find((b) => b.textContent && b.textContent.includes('Shadow Occlusion'));
    if (sub) sub.click();
  });
  await sleep(1500);
  await page.screenshot({ path: path.join(OUT_DIR, '05_experiments_shadow.png') });
  console.log('Saved 05_experiments_shadow.png');

  // 6. Open Saved Runs modal
  console.log('Opening Saved Runs Modal...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const saved = btns.find((b) => b.textContent && b.textContent.includes('Saved'));
    if (saved) saved.click();
  });
  await sleep(2000);
  await page.screenshot({ path: path.join(OUT_DIR, '06_saved_runs_modal.png') });
  console.log('Saved 06_saved_runs_modal.png');

  // Close modal with Escape
  await page.keyboard.press('Escape');
  await sleep(1000);

  // 7. Open Swagger Docs on FastAPI backend
  console.log('Navigating to FastAPI Swagger UI http://127.0.0.1:8000/docs ...');
  await page.goto('http://127.0.0.1:8000/docs', { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(2500);
  await page.screenshot({ path: path.join(OUT_DIR, '07_swagger_api_docs.png') });
  console.log('Saved 07_swagger_api_docs.png');

  await browser.close();
  console.log('All screenshots captured successfully!');
}

capture().catch((err) => {
  console.error('Capture error:', err);
  process.exit(1);
});
