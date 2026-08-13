/*=========================================================
    GERMAINE TRAINING INSTITUTE — PROGRAMME DATA
    Source: Official GTI Course Prospectus (Brochure 2022–2026)
    Used by course-detail.html to render a full prospectus-style
    page for each featured programme via ?course=<slug>
=========================================================*/

const courseCatalog = {

    "diploma-ict": {
        title: "Diploma in Information Communication Technology (ICT)",
        school: "School of Computing & Informatics",
        schoolPage: "courses-computing-it.html",
        qualification: "Diploma",
        levelClass: "diploma",
        duration: "2 Years (8 Terms)",
        fee: "KES 11,500",
        feePeriod: "per term",
        feeRaw: 11500,
        examBody: "KNEC",
        entryGrade: "C- and above",
        intake: "January / May / September",
        mode: "Full-Time / Part-Time / Weekend",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/schools/ict.jpg",
        summary: "Build real-world skills in networking, systems support and software use for the digital economy.",
        overview: {
            whatItIs: "The Diploma in ICT equips learners with a broad, hands-on foundation in computer systems, networking, software applications and digital infrastructure, preparing them to support and maintain ICT systems in any modern organisation.",
            whoFor: "Ideal for KCSE graduates who enjoy working with computers and technology and want a practical, industry-recognised pathway into the ICT sector, whether for employment or further study.",
            careerOutlook: "Graduates take up roles in ICT support, systems administration, networking and software-driven business environments across banking, government, telecoms and private enterprise.",
            learningOutcomes: [
                "Install, configure and troubleshoot computer hardware and networks",
                "Apply office productivity and business software confidently",
                "Understand database, systems and web fundamentals",
                "Apply cyber-security best practice in a workplace setting",
                "Support end-users and manage basic IT infrastructure"
            ]
        },
        units: [
            { semester: "Year 1, Term 1", unit: "Introduction to Computing & Computer Applications" , code: "DICT101" },
            { semester: "Year 1, Term 1", unit: "Computer Hardware & Maintenance" , code: "DICT102" },
            { semester: "Year 1, Term 2", unit: "Networking Fundamentals" , code: "DICT103" },
            { semester: "Year 1, Term 2", unit: "Operating Systems" , code: "DICT104" },
            { semester: "Year 2, Term 1", unit: "Database Systems" , code: "DICT105" },
            { semester: "Year 2, Term 1", unit: "Web Development" , code: "DICT106" },
            { semester: "Year 2, Term 2", unit: "Systems Analysis & Design" , code: "DICT107" },
            { semester: "Year 2, Term 2", unit: "Cyber Security Essentials & Industrial Attachment" , code: "DICT108" }
        ],
        careers: [
            "ICT Support Officer",
            "Network Technician",
            "Systems Administrator",
            "Web Developer",
            "Database Administrator",
            "IT Business Analyst"
        ],
        entryRequirements: [
            "KCSE Mean Grade C- (minus) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Mature entry candidates considered on merit"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per term)", amount: 11500, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 2000, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-data-management-analytics", "certificate-electrical-electronic", "diploma-business-management", "diploma-journalism-media"]
    },

    "diploma-business-management": {
        title: "Diploma in Business Management",
        school: "School of Business & Commerce",
        schoolPage: "courses-business-commerce.html",
        qualification: "Diploma",
        levelClass: "diploma",
        duration: "2 Years (8 Terms)",
        fee: "KES 11,500",
        feePeriod: "per term",
        feeRaw: 11500,
        examBody: "KNEC",
        entryGrade: "C- and above",
        intake: "January / May / September",
        mode: "Full-Time / Part-Time / Weekend",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/schools/business.jpg",
        summary: "Develop the management, finance and leadership skills demanded by modern employers and entrepreneurs.",
        overview: {
            whatItIs: "The Diploma in Business Management builds a strong foundation in management principles, finance, marketing and organisational leadership, giving learners the tools to manage teams, resources and operations effectively.",
            whoFor: "Suited to learners who want to run their own enterprise, join the corporate world, or grow into supervisory and management roles across any industry.",
            careerOutlook: "Graduates move into operations, administration, sales, marketing and entrepreneurship roles, with a clear pathway to further professional study.",
            learningOutcomes: [
                "Apply core principles of management and organisational behaviour",
                "Prepare basic financial and business records",
                "Plan and execute marketing and sales strategies",
                "Demonstrate leadership and business communication skills",
                "Develop and manage a business plan"
            ]
        },
        units: [
            { semester: "Year 1, Term 1", unit: "Principles of Management" , code: "DBM101" },
            { semester: "Year 1, Term 1", unit: "Business Communication" , code: "DBM102" },
            { semester: "Year 1, Term 2", unit: "Principles of Accounts" , code: "DBM103" },
            { semester: "Year 1, Term 2", unit: "Economics" , code: "DBM104" },
            { semester: "Year 2, Term 1", unit: "Marketing" , code: "DBM105" },
            { semester: "Year 2, Term 1", unit: "Entrepreneurship" , code: "DBM106" },
            { semester: "Year 2, Term 2", unit: "Human Resource Management" , code: "DBM107" },
            { semester: "Year 2, Term 2", unit: "Office Administration & Industrial Attachment" , code: "DBM108" }
        ],
        careers: [
            "Business Development Officer",
            "Administrative Officer",
            "Sales & Marketing Executive",
            "Operations Supervisor",
            "Entrepreneur",
            "Customer Relations Officer"
        ],
        entryRequirements: [
            "KCSE Mean Grade C- (minus) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Mature entry candidates considered on merit"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per term)", amount: 11500, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 1000, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-community-development", "diploma-data-management-analytics", "diploma-catering-accommodation", "diploma-ict"]
    },

    "diploma-catering-accommodation": {
        title: "Diploma in Catering & Accommodation Management",
        school: "School of Hospitality & Tourism",
        schoolPage: "courses-hospitality-tourism.html",
        qualification: "Diploma",
        levelClass: "diploma",
        duration: "27 Months (9 Terms)",
        fee: "KES 14,500",
        feePeriod: "per term",
        feeRaw: 14500,
        examBody: "KNEC",
        entryGrade: "C- and above",
        intake: "January / May / September",
        mode: "Full-Time / Weekend",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/schools/hospitality.jpg",
        summary: "Train in professional kitchen, front-office and accommodation operations for the hospitality industry.",
        overview: {
            whatItIs: "This diploma prepares learners for supervisory careers in hotels, restaurants and accommodation facilities, combining food production, front-office operations and hospitality management theory with extensive practical kitchen and hotel-floor training.",
            whoFor: "Ideal for learners passionate about food, guest service and hotel operations who want a recognised qualification for the fast-growing hospitality and tourism sector.",
            careerOutlook: "Graduates are absorbed into hotels, restaurants, lodges and resorts across Kenya and the region, with strong demand for trained catering and accommodation staff.",
            learningOutcomes: [
                "Prepare and present food to professional catering standards",
                "Manage front-office and accommodation operations",
                "Apply food safety and hygiene practices",
                "Handle guest relations and hospitality customer service",
                "Supervise catering and accommodation teams"
            ]
        },
        units: [
            { semester: "Year 1, Term 1", unit: "Food Production Fundamentals" , code: "DCAM101" },
            { semester: "Year 1, Term 1", unit: "Food & Beverage Service" , code: "DCAM102" },
            { semester: "Year 1, Term 2", unit: "Front Office Operations" , code: "DCAM103" },
            { semester: "Year 1, Term 2", unit: "Housekeeping & Accommodation" , code: "DCAM104" },
            { semester: "Year 2, Term 1", unit: "Catering Science & Nutrition" , code: "DCAM105" },
            { semester: "Year 2, Term 1", unit: "Hospitality Management" , code: "DCAM106" },
            { semester: "Year 2, Term 2", unit: "Events & Banqueting Operations" , code: "DCAM107" },
            { semester: "Year 3, Term 1", unit: "Industrial Attachment" , code: "DCAM108" }
        ],
        careers: [
            "Hotel & Accommodation Manager",
            "Executive Chef / Chef de Partie",
            "Catering Supervisor",
            "Front Office Manager",
            "Events & Banqueting Coordinator",
            "Restaurant Manager"
        ],
        entryRequirements: [
            "KCSE Mean Grade C- (minus) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Mature entry candidates considered on merit"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per term)", amount: 14500, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 2000, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-cosmetology", "diploma-journalism-media", "diploma-business-management", "diploma-community-development"]
    },

    "diploma-journalism-media": {
        title: "Diploma in Journalism & Media Studies",
        school: "School of Mass Communication & Journalism",
        schoolPage: "courses-mass-communication-journalism.html",
        qualification: "Diploma",
        levelClass: "diploma",
        duration: "12 Months (4 Terms)",
        fee: "KES 12,000",
        feePeriod: "per term",
        feeRaw: 12000,
        examBody: "ICM",
        entryGrade: "C- and above",
        intake: "January / May / September",
        mode: "Full-Time / Weekend",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/schools/journalism.jpg",
        summary: "Master news writing, media production and digital storytelling for print, broadcast and online media.",
        overview: {
            whatItIs: "This diploma covers news writing and reporting, media production, media law and ethics, and digital/social media practice, giving learners the practical skills used in modern newsrooms and media houses.",
            whoFor: "Suited to learners with a passion for storytelling, current affairs and media production who want a fast, focused route into journalism and communications careers.",
            careerOutlook: "Graduates work in print, broadcast, digital newsrooms, public relations firms and corporate communications departments.",
            learningOutcomes: [
                "Research, write and edit news and feature stories",
                "Operate audio, video and photographic equipment for media production",
                "Apply media law and ethical standards",
                "Produce content for digital and social media platforms",
                "Present and package stories for print or broadcast"
            ]
        },
        units: [
            { semester: "Term 1", unit: "Introduction to Journalism & Media Studies" , code: "DJM101" },
            { semester: "Term 1", unit: "News Writing & Reporting" , code: "DJM102" },
            { semester: "Term 2", unit: "Media Law & Ethics" , code: "DJM103" },
            { semester: "Term 2", unit: "Photojournalism & Videography" , code: "DJM104" },
            { semester: "Term 3", unit: "Broadcast Journalism" , code: "DJM105" },
            { semester: "Term 3", unit: "Digital & Social Media Practice" , code: "DJM106" },
            { semester: "Term 4", unit: "Public Relations & Corporate Communication" , code: "DJM107" },
            { semester: "Term 4", unit: "Media Attachment / Practicum" , code: "DJM108" }
        ],
        careers: [
            "Broadcast Journalist",
            "News Reporter / Editor",
            "Content Producer",
            "Public Relations Officer",
            "Digital Media Manager",
            "Corporate Communications Officer"
        ],
        entryRequirements: [
            "KCSE Mean Grade C- (minus) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Mature entry candidates considered on merit"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per term)", amount: 12000, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 1500, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-catering-accommodation", "diploma-community-development", "diploma-cosmetology", "diploma-ict"]
    },

    "diploma-cosmetology": {
        title: "Diploma in Cosmetology (Beauty Therapy & Hair Dressing)",
        school: "School of Cosmetology, Modern Fashion & Design",
        schoolPage: "courses-cosmetology-fashion-design.html",
        qualification: "Diploma",
        levelClass: "diploma",
        duration: "12 Months (4 Terms)",
        fee: "KES 15,000",
        feePeriod: "per term",
        feeRaw: 15000,
        examBody: "JP-UK",
        entryGrade: "C- and above",
        intake: "January / May / September",
        mode: "Full-Time / Part-Time",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/schools/cosmetology.jpg",
        summary: "Combine hair dressing and beauty therapy training into one internationally-recognised qualification.",
        overview: {
            whatItIs: "This diploma merges hair dressing and beauty therapy into a single comprehensive qualification, covering hairstyling, skin care, spa treatments and salon business practice using modern beauty labs and equipment.",
            whoFor: "Ideal for creative learners who want a hands-on career in the beauty industry, whether employed in a salon/spa or running their own beauty business.",
            careerOutlook: "Graduates work in salons, spas and beauty houses, or start their own cosmetology enterprises, with an internationally recognised JP-UK certification.",
            learningOutcomes: [
                "Perform professional hairdressing and styling techniques",
                "Carry out skin, spa and beauty therapy treatments",
                "Apply hygiene and safety standards in salon practice",
                "Advise clients on beauty and grooming needs",
                "Manage a salon or beauty business"
            ]
        },
        units: [
            { semester: "Term 1", unit: "Salon Hygiene & Client Care" , code: "DCOS101" },
            { semester: "Term 1", unit: "Hair Cutting & Styling" , code: "DCOS102" },
            { semester: "Term 2", unit: "Hair Colouring & Treatments" , code: "DCOS103" },
            { semester: "Term 2", unit: "Skin Care & Facial Treatments" , code: "DCOS104" },
            { semester: "Term 3", unit: "Manicure, Pedicure & Nail Art" , code: "DCOS105" },
            { semester: "Term 3", unit: "Spa & Body Treatments" , code: "DCOS106" },
            { semester: "Term 4", unit: "Makeup Artistry" , code: "DCOS107" },
            { semester: "Term 4", unit: "Salon Business Management / Attachment" , code: "DCOS108" }
        ],
        careers: [
            "Salon / Spa Manager",
            "Professional Hairstylist",
            "Beauty Therapist",
            "Makeup Artist",
            "Nail Technician",
            "Beauty Business Owner"
        ],
        entryRequirements: [
            "KCSE Mean Grade C- (minus) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Mature entry candidates considered on merit"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per term)", amount: 15000, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 2000, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-catering-accommodation", "diploma-journalism-media", "certificate-electrical-electronic", "diploma-business-management"]
    },

    "certificate-electrical-electronic": {
        title: "Certificate in Electrical & Electronic Installation",
        school: "School of Computing & Informatics",
        schoolPage: "courses-engineering-technology.html",
        qualification: "Certificate",
        levelClass: "certificate",
        duration: "1 Year (4 Terms)",
        fee: "KES 14,500",
        feePeriod: "per term",
        feeRaw: 14500,
        examBody: "KNEC",
        entryGrade: "D (plain) and above",
        intake: "January / May / September",
        mode: "Full-Time / Part-Time",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/schools/construction.jpg",
        summary: "Gain hands-on electrical installation and wiring skills recognised across the construction industry.",
        overview: {
            whatItIs: "This certificate trains learners in electrical wiring, installation and maintenance practices used in residential, commercial and light industrial settings, with strong emphasis on workshop practicals and safety.",
            whoFor: "Ideal for KCSE graduates who want a fast, practical route into the electrical trade, including those progressing toward the Electrical Wireman (EWM) grades.",
            careerOutlook: "Graduates find work as electrical installers, maintenance technicians and contractors, or progress to the Diploma in Electrical & Electronic Installation.",
            learningOutcomes: [
                "Carry out safe electrical wiring and installation work",
                "Read and interpret electrical drawings and diagrams",
                "Test, maintain and troubleshoot electrical installations",
                "Apply occupational health and safety standards",
                "Prepare for progression to Diploma-level electrical studies"
            ]
        },
        units: [
            { semester: "Term 1", unit: "Basic Electrical Principles" , code: "CEEI101" },
            { semester: "Term 1", unit: "Workshop Safety Practice" , code: "CEEI102" },
            { semester: "Term 2", unit: "Domestic Wiring & Installation" , code: "CEEI103" },
            { semester: "Term 2", unit: "Electrical Drawing" , code: "CEEI104" },
            { semester: "Term 3", unit: "Commercial & Industrial Wiring" , code: "CEEI105" },
            { semester: "Term 3", unit: "Electrical Machines" , code: "CEEI106" },
            { semester: "Term 4", unit: "Installation Testing & Maintenance" , code: "CEEI107" },
            { semester: "Term 4", unit: "Industrial Attachment" , code: "CEEI108" }
        ],
        careers: [
            "Electrical Installer / Technician",
            "Maintenance Electrician",
            "Electrical Contractor",
            "Panel Wireman",
            "Site Electrical Supervisor"
        ],
        entryRequirements: [
            "KCSE Mean Grade D (plain) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Mature entry candidates considered on merit"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per term)", amount: 14500, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 2000, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-ict", "diploma-data-management-analytics", "diploma-community-development", "diploma-catering-accommodation"]
    },

    "diploma-data-management-analytics": {
        title: "Diploma in Data Management & Analytics (DDMA)",
        school: "School of Computing & Informatics (KASNEB)",
        schoolPage: "courses-computing-it.html",
        qualification: "Diploma",
        levelClass: "diploma",
        duration: "8 Months (2 Levels)",
        fee: "KES 16,500",
        feePeriod: "per semester",
        feeRaw: 16500,
        examBody: "KASNEB",
        entryGrade: "D+ and above",
        intake: "January / May / September",
        mode: "Full-Time / Weekend",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/campus/computer-lab.jpg",
        summary: "A KASNEB-examined diploma in data handling, analytics and information systems for the data-driven economy.",
        overview: {
            whatItIs: "The KASNEB Diploma in Data Management & Analytics (DDMA) trains learners to collect, organise, analyse and present data using modern tools, covering two progressive levels examined directly by KASNEB.",
            whoFor: "Suited to learners with an interest in data, statistics and information systems who want a professional, nationally examined qualification recognised by employers across Kenya.",
            careerOutlook: "Graduates take up data-related roles across banking, government, NGOs and private companies increasingly reliant on data for decision-making.",
            learningOutcomes: [
                "Collect, clean and manage structured data sets",
                "Apply statistical and analytical tools to business data",
                "Design and query relational databases",
                "Present data through reports and dashboards",
                "Apply data governance and information security principles"
            ]
        },
        units: [
            { semester: "Level 1", unit: "Introduction to Data Management" , code: "DDMA101" },
            { semester: "Level 1", unit: "Business Statistics" , code: "DDMA102" },
            { semester: "Level 1", unit: "Database Design & SQL" , code: "DDMA103" },
            { semester: "Level 1", unit: "Information Communication Technology" , code: "DDMA104" },
            { semester: "Level 2", unit: "Data Analytics Techniques" , code: "DDMA105" },
            { semester: "Level 2", unit: "Data Visualisation & Reporting" , code: "DDMA106" },
            { semester: "Level 2", unit: "Systems & Data Security" , code: "DDMA107" },
            { semester: "Level 2", unit: "Research Project" , code: "DDMA108" }
        ],
        careers: [
            "Data Analyst",
            "Database Administrator",
            "Systems Administrator",
            "IT Support Officer",
            "Management Information Systems (MIS) Officer",
            "Business Intelligence Assistant"
        ],
        entryRequirements: [
            "KCSE Mean Grade D+ (plus) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Single-subject registration available for KASNEB units"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per semester)", amount: 16500, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 1500, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-ict", "certificate-electrical-electronic", "diploma-business-management", "diploma-community-development"]
    },

    "diploma-community-development": {
        title: "Diploma in Community Development",
        school: "School of Social Sciences",
        schoolPage: "courses-social-sciences.html",
        qualification: "Diploma",
        levelClass: "diploma",
        duration: "2 Years (8 Terms)",
        fee: "KES 11,500",
        feePeriod: "per term",
        feeRaw: 11500,
        examBody: "KNEC",
        entryGrade: "C- and above",
        intake: "January / May / September",
        mode: "Full-Time / Weekend",
        campus: "Nakuru — Pioneer Plaza",
        image: "assets/images/schools/graduate1.jpg",
        summary: "Prepare for a rewarding career driving grassroots development, social work and community programmes.",
        overview: {
            whatItIs: "This diploma trains learners in community mobilisation, project planning and social development theory, preparing them to design, implement and evaluate development programmes at the grassroots level.",
            whoFor: "Suited to learners passionate about social impact who want to work with communities, NGOs, government agencies or faith-based organisations.",
            careerOutlook: "Graduates are employed by NGOs, community-based organisations, county governments and development agencies working on social and economic empowerment programmes.",
            learningOutcomes: [
                "Plan, implement and evaluate community development projects",
                "Apply participatory community mobilisation techniques",
                "Understand social welfare and development policy",
                "Prepare project proposals and reports",
                "Facilitate group and community engagement processes"
            ]
        },
        units: [
            { semester: "Year 1, Term 1", unit: "Introduction to Community Development" , code: "DCD101" },
            { semester: "Year 1, Term 1", unit: "Sociology & Social Change" , code: "DCD102" },
            { semester: "Year 1, Term 2", unit: "Community Mobilisation" , code: "DCD103" },
            { semester: "Year 1, Term 2", unit: "Project Planning & Management" , code: "DCD104" },
            { semester: "Year 2, Term 1", unit: "Monitoring & Evaluation" , code: "DCD105" },
            { semester: "Year 2, Term 1", unit: "Gender & Development" , code: "DCD106" },
            { semester: "Year 2, Term 2", unit: "Counselling Skills" , code: "DCD107" },
            { semester: "Year 2, Term 2", unit: "Fieldwork / Industrial Attachment" , code: "DCD108" }
        ],
        careers: [
            "Community Development Officer",
            "Social Worker",
            "NGO Programme Officer",
            "Project Coordinator",
            "Monitoring & Evaluation Assistant",
            "Youth & Gender Officer"
        ],
        entryRequirements: [
            "KCSE Mean Grade C- (minus) and above",
            "Copies of previous academic certificates",
            "Copy of National ID / Birth Certificate",
            "2 recent passport-size photographs",
            "Mature entry candidates considered on merit"
        ],
        feeItems: [
            { item: "Registration Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Tuition Fee (per term)", amount: 11500, type: "recurring" },
            { item: "Library Fee (one-time)", amount: 1000, type: "onetime" },
            { item: "Examination Fee", amount: 1500, type: "recurring" },
            { item: "Practical / Lab Fee", amount: 1000, type: "recurring" },
            { item: "Student ID Card (one-time)", amount: 500, type: "onetime" }
        ],
        related: ["diploma-journalism-media", "diploma-business-management", "diploma-ict", "certificate-electrical-electronic"]
    }

};

/* Shared, programme-independent content */
const courseFeatures = [
    { icon: "fa-briefcase", label: "Industrial Attachment" },
    { icon: "fa-screwdriver-wrench", label: "Practical Training" },
    { icon: "fa-flask", label: "Modern Laboratories" },
    { icon: "fa-chalkboard-user", label: "Experienced Trainers" },
    { icon: "fa-certificate", label: "Industry Certification" },
    { icon: "fa-handshake-angle", label: "Career Support" }
];

const applySteps = [
    { icon: "fa-clipboard-list", title: "Choose Programme", text: "Browse our schools and select the programme that fits your career goals." },
    { icon: "fa-laptop", title: "Complete Online Application", text: "Fill in the online application form with your personal and academic details." },
    { icon: "fa-file-arrow-up", title: "Upload Required Documents", text: "Provide certificates, ID/birth certificate and passport photos." },
    { icon: "fa-magnifying-glass", title: "Admission Review", text: "Our admissions team reviews your application and documents for eligibility." },
    { icon: "fa-envelope-open-text", title: "Receive Admission Letter", text: "Successful applicants are issued an official admission letter." },
    { icon: "fa-people-group", title: "Registration & Orientation", text: "Complete registration, pay admission fees and attend orientation to begin training." }
];
