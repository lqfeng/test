// scripts/create_star_lists.js
// Create per-topic star lists from the exported starred_repos_classified.json

const fs = require('fs');
const path = require('path');

function loadExport(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(raw);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function main() {
  const input = path.resolve(process.cwd(), 'starred_repos_classified.json');
  if (!fs.existsSync(input)) {
    console.error('Input file not found:', input);
    process.exit(2);
  }

  const data = loadExport(input);
  if (!Array.isArray(data.repos)) {
    console.error('Invalid export format: missing repos array');
    process.exit(2);
  }

  const byTopic = {};
  data.repos.forEach(repo => {
    const topics = Array.isArray(repo.inferred_topics) && repo.inferred_topics.length ? repo.inferred_topics : ['Misc'];
    topics.forEach(t => {
      if (!byTopic[t]) byTopic[t] = [];
      byTopic[t].push({ name: repo.name, url: repo.html_url, language: repo.language, stars: repo.stargazers_count });
    });
  });

  const outDir = path.resolve(process.cwd(), 'starred_by_topic');
  ensureDir(outDir);

  // Write JSON per topic and a summary
  Object.keys(byTopic).forEach(topic => {
    const list = byTopic[topic];
    const fn = path.join(outDir, `${topic.replace(/[^a-z0-9\-]/gi, '_')}.json`);
    fs.writeFileSync(fn, JSON.stringify(list, null, 2), 'utf8');
    console.log('Wrote', fn, '(', list.length, 'repos)');
  });

  // Summary
  const summary = Object.fromEntries(Object.keys(byTopic).map(t => [t, byTopic[t].length]));
  fs.writeFileSync(path.join(outDir, 'SUMMARY.json'), JSON.stringify(summary, null, 2), 'utf8');
  console.log('Wrote summary');
}

if (require.main === module) main();
