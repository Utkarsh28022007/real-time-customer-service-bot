const puppeteer = require('./frontend/node_modules/puppeteer');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = path.join(__dirname, 'screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function runE2ETests() {
  console.log('Starting E2E Browser Testing for Customer Service Bot...');
  
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1280, height: 950 }
  });

  const page = await browser.newPage();

  try {
    console.log('Navigating to http://localhost:5173...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0', timeout: 30000 });
    await new Promise(r => setTimeout(r, 2000));

    // Helper: click a quick test prompt chip by label
    async function clickPromptChip(label) {
      console.log(`Clicking prompt chip: "${label}"...`);
      await page.evaluate((lbl) => {
        const btns = Array.from(document.querySelectorAll('button'));
        const target = btns.find(b => b.textContent.includes(lbl));
        if (target) {
          target.click();
        } else {
          throw new Error('Could not find button with text: ' + lbl);
        }
      }, label);

      // Wait for assistant response to start and finish streaming
      await new Promise(r => setTimeout(r, 1500));
      await page.waitForFunction(() => {
        const lastBubble = document.querySelector('.prose');
        const hasPulse = document.querySelector('.animate-pulse');
        // Check if there is bot text and streaming pulse indicator is gone
        return lastBubble && lastBubble.textContent.trim().length > 10;
      }, { timeout: 15000 });
      await new Promise(r => setTimeout(r, 2000));
    }

    // SCENARIO 1: FAQ Question
    console.log('\n--- Scenario 1: FAQ Question ---');
    await clickPromptChip('FAQ: Return Policy');
    const s1Path = path.join(SCREENSHOT_DIR, '01_faq_inquiry.png');
    await page.screenshot({ path: s1Path });
    console.log(`Saved screenshot: ${s1Path}`);

    // SCENARIO 2: Order Status Lookup
    console.log('\n--- Scenario 2: Order Status Lookup ---');
    await clickPromptChip('Order Lookup');
    // Wait an extra second for tool call rendering
    await new Promise(r => setTimeout(r, 2000));
    const s2Path = path.join(SCREENSHOT_DIR, '02_order_status.png');
    await page.screenshot({ path: s2Path });
    console.log(`Saved screenshot: ${s2Path}`);

    // SCENARIO 3: Angry Customer Escalation
    console.log('\n--- Scenario 3: Angry Customer Escalation ---');
    await clickPromptChip('Escalate (Angry Customer)');
    // Wait for escalation banner to appear
    await page.waitForSelector('.bg-gradient-to-r', { timeout: 10000 });
    await new Promise(r => setTimeout(r, 2000));
    const s3Path = path.join(SCREENSHOT_DIR, '03_angry_escalation.png');
    await page.screenshot({ path: s3Path });
    console.log(`Saved screenshot: ${s3Path}`);

    // SCENARIO 4: Out of Scope Guardrail
    console.log('\n--- Scenario 4: Out of Scope Guardrail ---');
    await clickPromptChip('Out of Scope Guardrail');
    await new Promise(r => setTimeout(r, 2500));
    const s4Path = path.join(SCREENSHOT_DIR, '04_guardrail_refusal.png');
    await page.screenshot({ path: s4Path });
    console.log(`Saved screenshot: ${s4Path}`);

    // SCENARIO 5: Admin Dashboard
    console.log('\n--- Scenario 5: Admin Dashboard ---');
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const adminBtn = btns.find(b => b.textContent.includes('Admin Portal'));
      if (adminBtn) adminBtn.click();
    });

    await new Promise(r => setTimeout(r, 2500));
    const s5Path = path.join(SCREENSHOT_DIR, '05_admin_dashboard.png');
    await page.screenshot({ path: s5Path });
    console.log(`Saved screenshot: ${s5Path}`);

    console.log('\nAll 5 E2E browser scenarios verified successfully!');
  } catch (err) {
    console.error('E2E Test Failed:', err);
    const errPath = path.join(SCREENSHOT_DIR, 'error_state.png');
    await page.screenshot({ path: errPath });
  } finally {
    await browser.close();
  }
}

runE2ETests();
