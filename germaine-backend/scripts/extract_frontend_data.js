/*
 * Extracts the two verified frontend data sources into plain JSON on
 * stdout, so the Python seed script (seed_catalogue.py) never has to
 * parse JavaScript itself. This is the ONLY place in the backend that
 * reads build10's data files directly.
 *
 * Usage:
 *   node extract_frontend_data.js /path/to/build10 > out.json
 *
 * Sources read (never modified):
 *   assets/js/school-data.js       -> window.SCHOOL_DATA / SCHOOL_ORDER
 *   assets/js/ai-courses-data.js   -> window.GermaineAICourses
 */

const path = require("path");
const fs = require("fs");

const buildRoot = process.argv[2];
if (!buildRoot) {
    console.error("Usage: node extract_frontend_data.js /path/to/build10");
    process.exit(1);
}

global.window = {};
global.document = { addEventListener: function () {} };

require(path.join(buildRoot, "assets/js/school-data.js"));
const SCHOOL_DATA = window.SCHOOL_DATA;
const SCHOOL_ORDER = window.SCHOOL_ORDER;

require(path.join(buildRoot, "assets/js/ai-courses-data.js"));
const aiData = window.GermaineAICourses;

process.stdout.write(JSON.stringify({
    schools: SCHOOL_DATA,
    school_order: SCHOOL_ORDER,
    ai_courses: aiData.courses,
    ai_categories: aiData.categories
}));
