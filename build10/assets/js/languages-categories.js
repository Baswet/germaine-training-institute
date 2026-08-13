/*==================================================
    GERMAINE — LANGUAGES & SHORT COURSES: CATEGORY METADATA

    Companion to assets/js/school-data.js. Holds the per-category
    overview copy, card image and career-opportunity lists for the
    Languages & Short Courses department, transcribed verbatim from
    the institute's "Languages & Short Courses July 26" source
    document.

    Programme rows themselves (name / duration / entry / fee) still
    live in SCHOOL_DATA.languages.programmes — this file only adds
    the surrounding context each category needs so the page can
    behave like an Academic School → Department page.

    `key` matches the `category` field on each programme, which is
    what scopes a category's table, entry requirements and careers
    to that category and nothing else.
==================================================*/
(function () {
    "use strict";

    /* ---------- shared CEFR ladder blurb ---------- */
    var LANG_INTRO = "The GTI department of languages is one of the most sought after sections. " +
        "The department offers global competent communication skills in different languages which are core " +
        "requirements for today's global communication. They connect you to multiple career opportunities globally. " +
        "Learning a foreign language greatly boosts your employability in NGOs, tourism, and international trade. " +
        "The duration for each level of training is three months.";

    /* Career list shared by every language track — taken from the
       "Career Opportunities on Qualification" list in the source doc. */
    var LANG_CAREERS = [
        "Take advantage of bilateral labour agreement between Kenya &amp; Foreign countries",
        "Aircraft flight attendant",
        "Hotel, tourism, and hospitality industry",
        "Foreign language trainer",
        "Study and settle in foreign country",
        "Sell/buy and transact in foreign language"
    ];

    window.LSC_CATEGORIES = [

        /*============ LANGUAGE CATEGORIES ============*/
        {
            key: "German",
            track: "language",
            name: "German",
            tagline: "CEFR A1 – C2 &middot; Goethe Institute pathway",
            image: "assets/images/schools/languages.jpg",
            description: "German is among the most marketable languages to study, opening doors through the " +
                "bilateral labour agreements between Kenya and Germany. Training runs from complete beginner (A1) " +
                "right through to full mastery (C2), with each level taking three months.",
            intro: LANG_INTRO,
            careers: LANG_CAREERS,
            quickLinks: [
                { label: "Goethe-Institut Kenya — Courses &amp; Exams", url: "https://www.goethe.de/ins/ke/en/index.html" },
                { label: "LinkedIn — German Language Jobs", url: "https://ke.linkedin.com/jobs/german-language-jobs" },
                { label: "BrighterMonday — German Speaking Jobs", url: "https://www.brightermonday.co.ke/jobs?q=german" }
            ]
        },
        {
            key: "French",
            track: "language",
            name: "French",
            tagline: "CEFR A1 – C2 &middot; Alliance Fran&ccedil;aise pathway",
            image: "assets/images/schools/languages-about-hero.webp",
            description: "French connects you to francophone Africa, Europe and Canada, and is highly valued " +
                "across NGOs, tourism and international trade. The programme ladders from beginner (A1) to " +
                "advanced mastery (C2), three months per level.",
            intro: LANG_INTRO,
            careers: LANG_CAREERS,
            quickLinks: [
                { label: "Alliance Fran&ccedil;aise Nairobi — Courses &amp; Exams", url: "https://www.alliancefrancaise.or.ke/" },
                { label: "LinkedIn — French Language Jobs", url: "https://ke.linkedin.com/jobs/french-language-jobs" },
                { label: "BrighterMonday — French Speaking Jobs", url: "https://www.brightermonday.co.ke/jobs?q=french" }
            ]
        },
        {
            key: "Chinese",
            track: "language",
            name: "Chinese (Mandarin)",
            tagline: "CEFR A1 – C1",
            image: "assets/images/schools/pexels-kampus-8629107.jpg",
            description: "Mandarin is one of the most strategically valuable languages in today's economy, " +
                "given China's role in Kenyan infrastructure, manufacturing and trade. Levels run from " +
                "beginner (A1) to advanced (C1), three months each.",
            intro: LANG_INTRO,
            careers: LANG_CAREERS,
            quickLinks: [
                { label: "Confucius Institute Kenya — Courses &amp; Exams", url: "https://www.confuciusinstitute.uonbi.ac.ke/" },
                { label: "LinkedIn — Mandarin / Chinese Language Jobs", url: "https://ke.linkedin.com/jobs/mandarin-jobs" },
                { label: "BrighterMonday — Chinese Speaking Jobs", url: "https://www.brightermonday.co.ke/jobs?q=chinese" }
            ]
        },
        {
            key: "English",
            track: "language",
            name: "English",
            tagline: "CEFR A1 – A2",
            image: "assets/images/schools/pexels-kgstudios-36520424.jpg",
            description: "English proficiency underpins employability across virtually every sector and is a " +
                "prerequisite for study and work abroad. Beginner (A1) and Elementary (A2) levels are offered, " +
                "three months per level.",
            intro: LANG_INTRO,
            careers: LANG_CAREERS,
            quickLinks: [
                { label: "British Council Kenya — English Exams", url: "https://www.britishcouncil.co.ke/exam" },
                { label: "LinkedIn — English Communication Jobs", url: "https://ke.linkedin.com/jobs/english-jobs" },
                { label: "BrighterMonday — Customer Service Jobs", url: "https://www.brightermonday.co.ke/jobs?q=customer%20service" }
            ]
        },

        /*============ SHORT COURSE CATEGORIES ============*/
        {
            key: "Medical",
            track: "short-course",
            name: "Medical",
            tagline: "Caregiving &middot; CNA &middot; Homecare",
            image: "assets/images/schools/health.jpg",
            description: "As Kenya expands and modernizes, driven by the twin challenge of a growing and aging " +
                "population, demand rises for professional medical caregivers and home managers. The Germaine " +
                "Medical department offers practical training for health care assistants, caregivers and homecare " +
                "managers &mdash; the first responders before a patient reaches a medical facility, and vital " +
                "support in hospitals, clinics, homes and care facilities.",
            careers: [
                "Home-based palliative care provider",
                "County health Volunteers (CHVs)",
                "Disability support worker",
                "Health care assistant (hospitals, clinics, nursing homes)",
                "NGO / programme field health worker",
                "Professional caregiver (private homes, care centres)",
                "Homecare professional for elderly",
                "Medical courier &amp; patient mobility (with driving)"
            ],
            quickLinks: [
                { label: "BrighterMonday — Healthcare &amp; Caregiving Jobs", url: "https://www.brightermonday.co.ke/jobs/healthcare" },
                { label: "LinkedIn — Caregiver Jobs Kenya", url: "https://ke.linkedin.com/jobs/caregiver-jobs" },
                { label: "MyJobMag — Medical &amp; Health Jobs", url: "https://www.myjobmag.co.ke/jobs-by-field/medical-health" }
            ]
        },
        {
            key: "Agriculture",
            track: "short-course",
            name: "Agriculture",
            tagline: "Greenhouse &middot; Hydroponics &middot; Farm machinery",
            image: "assets/images/schools/agriculture.jpg",
            description: "Agriculture remains the main pillar of the Kenyan economy, and modernizing farming " +
                "increasingly depends on skilled manpower who can maintain tools, machinery and agricultural " +
                "systems. Our agricultural department offers on-site practical training preparing trainees for " +
                "immediate employment on farms, in agribusiness, and with NGOs and county governments &mdash; " +
                "covering irrigation systems installation, hydroponics and greenhouse management.",
            careers: [
                "Agronomist / Organic farming entrepreneur",
                "Orchard manager",
                "Farm tractor mechanic",
                "Farm tools &amp; equipment repair technician",
                "Agribusiness equipment service provider",
                "Greenhouse / hydroponics system technician",
                "Nursery manager &amp; horticultural technician",
                "Irrigation installation &amp; maintenance contractor",
                "Landscape designer &amp; garden maintenance professional",
                "County government agriculture mechanization officer"
            ],
            quickLinks: [
                { label: "BrighterMonday — Agriculture Jobs", url: "https://www.brightermonday.co.ke/jobs/agriculture" },
                { label: "LinkedIn — Agriculture Jobs Kenya", url: "https://ke.linkedin.com/jobs/agriculture-jobs" },
                { label: "MyJobMag — Agricultural &amp; Farming Jobs", url: "https://www.myjobmag.co.ke/jobs-by-field/agricultural-farming" }
            ]
        },
        {
            key: "Catering & Accommodation",
            track: "short-course",
            name: "Catering &amp; Accommodation",
            tagline: "Kitchen &middot; Service &middot; Pastry &middot; Housekeeping",
            image: "assets/images/schools/hospitality.jpg",
            description: "The catering and hotel industry spans the entire globe, offering on-demand career " +
                "opportunities for skilled hospitality professionals. Our hospitality section prepares trainees " +
                "for careers in kitchens, restaurants, hotels, catering companies, bakeries and events, both " +
                "locally and internationally. The structured programme lets trainees join at their desired level " +
                "and progress steadily to mastery.",
            careers: [
                "Supermarket / food court Chef",
                "Cruise ship &amp; airline cabin crew (with further skilling)",
                "Pastry chef &amp; baker",
                "Food &amp; Beverage Production manager",
                "Events caterer &amp; catering entrepreneur",
                "Bakery &amp; confectionery business owner",
                "Chef / Sous Chef (hotels, restaurants, safari lodges)",
                "Food processing entrepreneur (sauces, dairy, spices)",
                "Waiter / head waiter (fine dining, hotels, events)",
                "Housekeeping supervisor (hotels, hospitals, lodges)",
                "Hotel &amp; lodge owner / manager (long-term pathway)"
            ],
            quickLinks: [
                { label: "BrighterMonday — Hospitality &amp; Catering Jobs", url: "https://www.brightermonday.co.ke/jobs/hospitality-leisure-sport" },
                { label: "LinkedIn — Hospitality Jobs Kenya", url: "https://ke.linkedin.com/jobs/hospitality-jobs" },
                { label: "MyJobMag — Catering &amp; Confectionery Jobs", url: "https://www.myjobmag.co.ke/jobs-by-field/catering-confectionery" }
            ]
        },
        {
            key: "Electrical & Electronics",
            track: "short-course",
            name: "Electrical &amp; Electronics",
            tagline: "Installation &middot; Solar PV &middot; CCTV &middot; Repair",
            image: "assets/images/schools/electrical-engineering.jpg",
            description: "Our Electrical &amp; Electronics department offers practical, hands-on training in " +
                "domestic and industrial electrical installation, solar PV, refrigeration, CCTV, phone repair and " +
                "home appliances. Courses are structured so trainees begin from basics and progress methodically " +
                "to advanced, specialist skills &mdash; making graduates immediately employable across every " +
                "sector, from construction to telecommunications to renewable energy.",
            careers: [
                "Dealer in electric accessories",
                "Domestic &amp; commercial electrician",
                "Solar PV installer &amp; system technician",
                "Home appliance repair technician",
                "CCTV &amp; security systems installer",
                "Audio / visual equipment repair specialist",
                "Electrical fitter (manufacturing, construction)",
                "Phone repair technician (shop owner or employed)",
                "Refrigeration &amp; air conditioning technician",
                "Industrial electronics &amp; control systems technician",
                "Electric fence installer"
            ],
            quickLinks: [
                { label: "CareerJet — Electrical Jobs Kenya", url: "https://www.careerjet.co.ke/electrical-jobs" },
                { label: "LinkedIn — Electrical Technician Jobs", url: "https://ke.linkedin.com/jobs/electrical-technician-jobs" },
                { label: "MyJobMag — Engineering &amp; Technical Jobs", url: "https://www.myjobmag.co.ke/jobs-by-field/engineering-technical" }
            ]
        },
        {
            key: "Computing & Informatics",
            track: "short-course",
            name: "Computing &amp; Informatics",
            tagline: "ICT &middot; Cyber Security &middot; Design &middot; Marketing",
            image: "assets/images/schools/ict.jpg",
            description: "We guarantee practical information technology training that leads to job opportunities " +
                "across a wide array of industries. Tailor-made courses range from computer literacy to advanced " +
                "networking, cyber security, graphic design, social media marketing and AI &mdash; structured for " +
                "total beginners and for those advancing existing digital skills. Well-equipped labs, current " +
                "software and industry-experienced instructors mean every trainee leaves with skills they can " +
                "apply immediately.",
            careers: [
                "Office administrator &amp; data entry professional",
                "Network administrator (SMEs)",
                "IT support technician (help desk)",
                "Cybersecurity analyst (entry level)",
                "Graphic designer &amp; brand visualiser",
                "Government &amp; NGO ICT officer",
                "Digital marketer (social media, SEO, content)",
                "Freelancer on global platforms (Upwork, Fiverr)",
                "Fibre optic installation &amp; maintenance technician",
                "Computer &amp; laptop repair technician / shop owner"
            ],
            quickLinks: [
                { label: "LinkedIn — ICT Jobs Kenya", url: "https://ke.linkedin.com/jobs/ict-jobs" },
                { label: "BrighterMonday — IT &amp; Software Jobs", url: "https://www.brightermonday.co.ke/jobs/it-software" },
                { label: "Fuzu — Technology Jobs", url: "https://www.fuzu.com/kenya/jobs/it-and-software" }
            ]
        },
        {
            key: "Building & Construction",
            track: "short-course",
            name: "Building &amp; Construction",
            tagline: "Masonry &middot; Plumbing &middot; ArchiCAD &middot; Finishes",
            image: "assets/images/schools/civil-building-department.jpg",
            description: "Kenya's construction industry has been energised by government infrastructure projects, " +
                "affordable housing and the rapid growth of residential and commercial property. Our Building &amp; " +
                "Construction department equips trainees with the range of skills that industry needs &mdash; from " +
                "trades such as masonry, carpentry and plumbing through to specialised areas like interior design, " +
                "glass fitting and scaffolding.",
            careers: [
                "Real estate developer entrepreneurship",
                "Welder &amp; steel fixer",
                "Gypsum &amp; drywall installer",
                "Interior designer &amp; decorator",
                "CABRO &amp; concrete moulder",
                "Glazier &amp; glass installation specialist",
                "Self-employed building contractor",
                "Construction site supervisor &amp; foreman",
                "Painter, sign writer &amp; finishes specialist",
                "Property caretaker &amp; facilities manager",
                "ArchiCAD draughtsperson / building technician",
                "Mason, carpenter, plumber, roofer, tiler (employed)"
            ],
            quickLinks: [
                { label: "BrighterMonday — Building &amp; Construction Jobs", url: "https://www.brightermonday.co.ke/jobs/building-architecture" },
                { label: "LinkedIn — Construction Jobs Kenya", url: "https://ke.linkedin.com/jobs/construction-jobs" },
                { label: "MyJobMag — Building &amp; Construction Jobs", url: "https://www.myjobmag.co.ke/jobs-by-field/building-construction" }
            ]
        },
        {
            key: "Mechanical & Motor Mechanics",
            track: "short-course",
            name: "Mechanical &amp; Motor Mechanics",
            tagline: "Vehicles &middot; Plant &middot; Welding &middot; Spray painting",
            image: "assets/images/schools/mechanical-engineering.jpg",
            description: "Our courses cover motor vehicles, construction plant, motorcycles, generators, welding " +
                "and spray painting among other trades. Each course builds from foundation level through to more " +
                "advanced training, so trainees can enter at the right point and progress to specialist mastery.",
            careers: [
                "Vehicle AC technician",
                "Panel beater &amp; spray painting technician",
                "Workshop supervisor / foreman",
                "Heavy machinery spare parts dealer",
                "Motorcycle mechanic &amp; workshop owner",
                "Welder &amp; fabrication specialist",
                "Motor vehicle mechanic (dealerships, garages, fleet)",
                "Generator &amp; stationary engine technician",
                "Construction plant / heavy equipment mechanics",
                "Automotive electronics &amp; diagnostics technician"
            ],
            quickLinks: [
                { label: "BrighterMonday — Automotive &amp; Mechanical Jobs", url: "https://www.brightermonday.co.ke/jobs/engineering-technical" },
                { label: "LinkedIn — Motor Vehicle Mechanic Jobs", url: "https://ke.linkedin.com/jobs/motor-vehicle-mechanic-jobs" },
                { label: "MyJobMag — Engineering &amp; Technical Jobs", url: "https://www.myjobmag.co.ke/jobs-by-field/engineering-technical" }
            ]
        }
    ];
})();
