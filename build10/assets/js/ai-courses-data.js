/*==================================================
    GERMAINE — AI BOOTCAMP COURSES DATA MODEL
    Single source of truth consumed by:
      - ai-bootcamp-courses.html (catalogue hub)
      - ai-course-*.html detail pages (via ai-course-detail-renderer.js)

    IMPORTANT — DATA HONESTY NOTE:
    All descriptive content below (overview, skills, projects,
    career outcomes, learning-format copy) is carried over verbatim
    or near-verbatim from the site's existing, already-published
    course pages. Durations are Germaine's own, already-established
    week counts and are unchanged here.

    Tuition fees and start dates were set by Germaine admissions
    using comparable regional bootcamp pricing as a benchmark, each
    reduced by a fixed KSh 5,000 margin. Every mode's fee/startDate
    is set explicitly per programme below (via the `pricing` param
    on modes()) rather than left as a placeholder. Where no reliable
    external benchmark existed for a given mode, "Contact Admissions"
    is kept rather than inventing a figure.
==================================================*/

(function (global) {
    "use strict";

    function modes(durationLabel, pricing) {
        pricing = pricing || {};
        return [
            {
                id: "ft-hybrid",
                label: "Full-time",
                sub: "Hybrid",
                icon: "fa-solid fa-building-user",
                duration: pricing.hybridDuration || durationLabel,
                startDate: pricing.hybridStart || "Contact Admissions",
                fee: pricing.hybridFee || "Contact Admissions",
                schedule: pricing.hybridSchedule || "Weekday classes on campus, blended with guided online sessions."
            },
            {
                id: "ft-remote",
                label: "Full-time",
                sub: "Remote",
                icon: "fa-solid fa-house-laptop",
                duration: pricing.remoteDuration || durationLabel,
                startDate: pricing.remoteStart || "Contact Admissions",
                fee: pricing.remoteFee || "Contact Admissions",
                schedule: pricing.remoteSchedule || "Weekday live online classes with the same full-time curriculum."
            },
            {
                id: "pt-remote",
                label: "Part-time",
                sub: "Remote",
                icon: "fa-solid fa-clock-rotate-left",
                duration: pricing.ptDuration || (durationLabel + " (extended pace)"),
                startDate: pricing.ptStart || "Contact Admissions",
                fee: pricing.ptFee || "Contact Admissions",
                schedule: pricing.ptSchedule || "Evening / weekend online classes for learners studying alongside work."
            }
        ];
    }

    function baseFaqs(courseName, completionText, extra) {
        var faqs = [
            {
                q: "What are the fees for this programme?",
                a: "Fees vary by learning mode and intake. Contact our admissions team on +254 719 488 112 or admissions@germaineinstitute.com for up-to-date fee information for " + courseName + "."
            },
            {
                q: "When does the next intake start?",
                a: "Contact our admissions team to confirm the next available start date for your preferred learning mode."
            },
            {
                q: "Can I switch between learning modes after enrolling?",
                a: "Speak with admissions about switching between Full-time and Part-time or between Hybrid and Remote after enrolment — options depend on cohort availability."
            },
            {
                q: "What do I get on completion?",
                a: completionText
            }
        ];
        if (extra) faqs.push(extra);
        return faqs;
    }

    var COURSES = [
        {
            slug: "ai-ml",
            file: "ai-course-ai-ml.html",
            category: "ai",
            categoryLabel: "Artificial Intelligence",
            eyebrowIcon: "fa-solid fa-brain",
            title: "Artificial Intelligence & Machine Learning",
            titleParts: ["Artificial Intelligence & ", "Machine Learning"],
            lead: "Master Generative AI, Prompt Engineering, Machine Learning, Computer Vision, Natural Language Processing, and AI deployment through hands-on projects.",
            duration: "16 Weeks",
            badgeNumber: "16",
            heroImage: "pics/ai-ml-hands-on.jpg",
            heroAlt: "Students working hands-on with AI tools in a Germaine computer lab",
            overview: "Artificial Intelligence is reshaping how organisations build products, serve customers, and make decisions. This programme takes you from core machine learning concepts through to generative AI, teaching you to design, train, evaluate, and deploy AI systems that solve real problems — not just complete tutorials. You will work with real datasets, modern AI tools, and guided mentorship from professionals already building AI systems in industry, finishing with a portfolio you can show employers.",
            whoFor: "Contact our admissions team to confirm entry requirements for this programme.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "Open to learners with a genuine interest in AI and machine learning; a STEM background or prior programming exposure helps but is assessed case-by-case." }
                ],
                recommended: [
                    { icon: "fa-brands fa-python", text: "Basic familiarity with Python or another programming language." },
                    { icon: "fa-solid fa-square-root-variable", text: "Comfort with foundational maths (algebra, basic statistics) is an advantage, though not assessed on entry." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run a modern code editor, Python, and common ML libraries." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for live sessions and cloud-based tools." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Build practical machine learning and generative AI skills",
                "Work on real projects across computer vision, NLP and AI deployment",
                "Develop a portfolio of deployed AI systems",
                "Prepare for AI/ML engineering and data science career paths"
            ],
            skills: [
                { icon: "fa-solid fa-robot", title: "Machine Learning Fundamentals", desc: "Supervised and unsupervised learning, model training and evaluation." },
                { icon: "fa-solid fa-comments", title: "Generative AI & Prompt Engineering", desc: "Design effective prompts and build applications on top of large language models." },
                { icon: "fa-solid fa-eye", title: "Computer Vision", desc: "Image classification, object detection, and visual recognition pipelines." },
                { icon: "fa-solid fa-language", title: "Natural Language Processing", desc: "Text processing, sentiment analysis, and language-model-powered applications." },
                { icon: "fa-solid fa-server", title: "AI Model Deployment", desc: "Package and ship AI models into working applications and APIs." },
                { icon: "fa-solid fa-scale-balanced", title: "Responsible & Ethical AI", desc: "Bias, fairness, data privacy and responsible-use considerations in AI systems." }
            ],
            projects: [
                { title: "Predictive Analytics Model", desc: "Train a machine learning model to forecast trends from real-world data." },
                { title: "AI Chatbot Assistant", desc: "Build a conversational assistant powered by a large language model." },
                { title: "Image Recognition App", desc: "Classify and detect objects in images using a computer vision pipeline." },
                { title: "Capstone AI Portfolio Project", desc: "Design, build and present a complete AI solution from concept to demo." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-robot", title: "AI / ML Engineer" },
                { icon: "fa-solid fa-database", title: "Data Scientist" },
                { icon: "fa-solid fa-keyboard", title: "AI Prompt Engineer" },
                { icon: "fa-solid fa-comment-dots", title: "NLP Engineer" },
                { icon: "fa-solid fa-eye", title: "Computer Vision Engineer" },
                { icon: "fa-solid fa-lightbulb", title: "AI Product Manager" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes combined with hands-on lab time." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Regular check-ins and feedback from working AI professionals." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified AI Practitioner credential on completion." }
            ],
            applyHeading: "Ready to Start Your AI Career?",
            applySubtext: "Applications for the next cohort are open now.",
            modes: modes("16 Weeks", {
                hybridFee: "KSh 145,000", hybridStart: "28th September 2026",
                hybridSchedule: "Guided classroom sessions with hands-on lab work | Mon, Tue & Thu, 6 PM – 9 PM E.A.T",
                remoteFee: "KSh 145,000", remoteStart: "28th September 2026",
                remoteSchedule: "100% remote classes | Mon, Tue & Thu, 6 PM – 9 PM E.A.T",
                ptFee: "KSh 145,000", ptStart: "28th September 2026",
                ptSchedule: "100% remote classes | Mon, Tue & Thu, 6 PM – 9 PM E.A.T, plus weekly independent lab work"
            }),
            faqs: baseFaqs("Artificial Intelligence & Machine Learning", "Earn a Germaine-Certified AI Practitioner credential on completion.")
        },
        {
            slug: "software-engineering",
            file: "ai-course-software-engineering.html",
            category: "software-engineering",
            categoryLabel: "Software Engineering",
            eyebrowIcon: "fa-solid fa-code",
            title: "Software Engineering",
            titleParts: ["Software ", "Engineering"],
            lead: "Learn modern full-stack software development using HTML, CSS, JavaScript, React, Python, Flask, SQL, APIs, Git, and cloud deployment while building production-ready applications.",
            duration: "20 Weeks",
            badgeNumber: "20",
            heroImage: "pics/software-engineering-lab.jpg",
            heroAlt: "Germaine software engineering students collaborating in a computer lab",
            overview: "This programme takes you from programming fundamentals through to building and deploying full-stack web applications. You'll learn to write clean, maintainable code, design databases, build APIs, and ship products using the same tools and workflows used by professional software teams — culminating in a portfolio of real applications you build yourself.",
            whoFor: "Contact our admissions team to confirm entry requirements for this programme.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "Open to learners ready for an Intermediate-level, project-based programme; prior coding exposure helps but is not mandatory to apply." }
                ],
                recommended: [
                    { icon: "fa-solid fa-code", text: "Familiarity with any programming language, even at a beginner level, helps you progress faster." },
                    { icon: "fa-solid fa-lightbulb", text: "Basic understanding of how websites or applications work is an advantage." }
                ],
                technical: [
                    { icon: "fa-brands fa-git-alt", text: "A laptop able to run a code editor, a local development environment, and Git." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for collaborative coding and deployment exercises." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Build full-stack web applications from front-end to back-end",
                "Work with the same tools and workflows used by professional teams",
                "Ship a portfolio of real, deployed applications",
                "Prepare for software engineering and developer career paths"
            ],
            skills: [
                { icon: "fa-brands fa-html5", title: "HTML, CSS & JavaScript", desc: "The core building blocks of every website and web application." },
                { icon: "fa-brands fa-react", title: "React & Modern Frontend", desc: "Build interactive, component-based user interfaces." },
                { icon: "fa-brands fa-python", title: "Python & Flask", desc: "Server-side programming and building web application backends." },
                { icon: "fa-solid fa-database", title: "SQL & Databases", desc: "Design, query and manage relational databases." },
                { icon: "fa-solid fa-plug", title: "APIs & Integrations", desc: "Build and consume REST APIs to connect applications and services." },
                { icon: "fa-brands fa-git-alt", title: "Git & Cloud Deployment", desc: "Version control, collaboration workflows, and shipping apps to the cloud." }
            ],
            projects: [
                { title: "Personal Portfolio Website", desc: "A responsive website showcasing your work, built from scratch." },
                { title: "Full-Stack Web Application", desc: "A complete application with a database-backed API and a React frontend." },
                { title: "REST API Service", desc: "A documented API that other developers or applications can consume." },
                { title: "Capstone Group Project", desc: "A production-ready application built and deployed in a small team." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-laptop-code", title: "Software Engineer" },
                { icon: "fa-solid fa-display", title: "Frontend Developer" },
                { icon: "fa-solid fa-server", title: "Backend Developer" },
                { icon: "fa-solid fa-layer-group", title: "Full-Stack Developer" },
                { icon: "fa-solid fa-bug", title: "QA / Test Engineer" },
                { icon: "fa-solid fa-diagram-project", title: "Junior Product Engineer" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes combined with hands-on coding labs." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Code reviews and feedback from experienced software engineers." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified Software Engineer credential on completion." }
            ],
            applyHeading: "Ready to Start Your Engineering Career?",
            applySubtext: "Applications for the next cohort are open now.",
            modes: modes("20 Weeks", {
                hybridFee: "KSh 195,000", hybridStart: "31st August 2026",
                hybridSchedule: "Online & physical classes on campus | Mon – Fri, 8 AM – 5 PM E.A.T",
                remoteFee: "KSh 169,000", remoteStart: "31st August 2026",
                remoteSchedule: "100% online classes | Mon – Fri, 8 AM – 5 PM E.A.T",
                ptFee: "KSh 195,000", ptStart: "31st August 2026",
                ptSchedule: "100% online classes | Mon – Fri, 6 PM – 9 PM E.A.T"
            }),
            faqs: baseFaqs("Software Engineering", "Earn a Germaine-Certified Software Engineer credential on completion.")
        },
        {
            slug: "cyber-security",
            file: "ai-course-cyber-security.html",
            category: "cyber-security",
            categoryLabel: "Cyber Security",
            eyebrowIcon: "fa-solid fa-shield-halved",
            title: "Cyber Security",
            titleParts: ["Cyber ", "Security"],
            lead: "Develop practical cybersecurity skills including networking, ethical hacking, penetration testing, digital forensics, cloud security, and incident response.",
            duration: "14 Weeks",
            badgeNumber: "14",
            heroImage: "pics/cybersecurity-hacker-workstation.jpg",
            heroAlt: "Student working at a laptop with live security data displayed behind them",
            overview: "As organisations move more of their operations online, the demand for people who can defend networks, applications and data keeps growing. This programme builds you from networking and security fundamentals up through ethical hacking, penetration testing and incident response, using realistic lab environments so you practice defending and testing systems the way security professionals actually do.",
            whoFor: "Contact our admissions team to confirm entry requirements for this programme.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "Designed as an Intermediate-level programme, best suited to learners with basic computer and networking literacy." },
                    { icon: "fa-solid fa-signpost", text: "Completely new to the field? Our Introduction to Cyber Security programme is the recommended starting point." }
                ],
                recommended: [
                    { icon: "fa-solid fa-network-wired", text: "Some familiarity with operating systems (Windows/Linux) and basic networking concepts is helpful." },
                    { icon: "fa-solid fa-lightbulb", text: "An analytical mindset and comfort working through technical troubleshooting scenarios." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run virtualization/lab software used in hands-on security exercises." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for lab environments and live sessions." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Build practical skills in ethical hacking and penetration testing",
                "Practice defending and testing systems in realistic lab environments",
                "Deliver a professional penetration-test report and incident-response simulation",
                "Prepare for security analyst and SOC career paths"
            ],
            skills: [
                { icon: "fa-solid fa-network-wired", title: "Networking Fundamentals", desc: "How networks, protocols and infrastructure actually work." },
                { icon: "fa-solid fa-user-secret", title: "Ethical Hacking", desc: "Legally test systems the way an attacker would to find weaknesses." },
                { icon: "fa-solid fa-bug-slash", title: "Penetration Testing", desc: "Structured testing methodology to uncover and report vulnerabilities." },
                { icon: "fa-solid fa-magnifying-glass", title: "Digital Forensics", desc: "Investigate and analyse security incidents after they occur." },
                { icon: "fa-solid fa-cloud-arrow-up", title: "Cloud Security", desc: "Securing infrastructure and data hosted in the cloud." },
                { icon: "fa-solid fa-triangle-exclamation", title: "Incident Response", desc: "Detect, contain and respond to active security threats." }
            ],
            projects: [
                { title: "Network Vulnerability Assessment", desc: "Scan and document weaknesses across a simulated network." },
                { title: "Penetration Test Report", desc: "Run a full penetration test and deliver a professional findings report." },
                { title: "Incident Response Simulation", desc: "Detect and respond to a simulated live security breach." },
                { title: "Security Hardening Capstone", desc: "Secure a vulnerable system end-to-end and document your process." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-user-shield", title: "Security Analyst" },
                { icon: "fa-solid fa-bug-slash", title: "Penetration Tester" },
                { icon: "fa-solid fa-network-wired", title: "Network Security Engineer" },
                { icon: "fa-solid fa-magnifying-glass", title: "Digital Forensics Analyst" },
                { icon: "fa-solid fa-cloud-arrow-up", title: "Cloud Security Specialist" },
                { icon: "fa-solid fa-headset", title: "SOC Analyst" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes with hands-on lab exercises in real tools." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Guidance and feedback from working security professionals." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified Cyber Security credential on completion." }
            ],
            applyHeading: "Ready to Start Your Security Career?",
            applySubtext: "Applications for the next cohort are open now.",
            modes: modes("14 Weeks", {
                hybridFee: "KSh 195,000", hybridStart: "7th September 2026",
                hybridSchedule: "Online & physical classes on campus | Mon – Fri, 8 AM – 5 PM E.A.T",
                remoteFee: "KSh 195,000", remoteStart: "7th September 2026",
                remoteSchedule: "100% remote classes | Mon – Fri, 8 AM – 5 PM E.A.T",
                ptFee: "KSh 195,000", ptStart: "7th September 2026",
                ptSchedule: "100% remote classes | Mon – Fri, 6 PM – 9 PM E.A.T"
            }),
            faqs: baseFaqs("Cyber Security", "Earn a Germaine-Certified Cyber Security credential on completion.")
        },
        {
            slug: "data-analytics",
            file: "ai-course-data-analytics.html",
            category: "data-analytics",
            categoryLabel: "Data Analytics",
            eyebrowIcon: "fa-solid fa-chart-line",
            title: "Data Analytics",
            titleParts: ["Data ", "Analytics"],
            lead: "Master Excel, SQL, Power BI, Python, dashboards, data visualisation, and business intelligence using real-world datasets.",
            duration: "12 Weeks",
            badgeNumber: "12",
            heroImage: "pics/data-analytics-visual.jpg",
            heroAlt: "Hands typing on a laptop with a data analytics visualisation overlay",
            overview: "Every organisation collects data, but few people know how to turn it into decisions. This programme teaches you to clean, analyse and visualise data using the tools most used in business today — Excel, SQL and Power BI — and to build the kind of dashboards and reports that help managers act with confidence, using real datasets rather than toy examples.",
            whoFor: "Contact our admissions team to confirm entry requirements for this programme.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "Open to learners building practical data analysis skills; no advanced maths background is required to apply." },
                    { icon: "fa-solid fa-user-check", text: "Intermediate-level pacing, so basic spreadsheet or data-handling experience is helpful." }
                ],
                recommended: [
                    { icon: "fa-solid fa-table", text: "Comfort working with spreadsheets (e.g. Excel) and an interest in working with numbers and trends." },
                    { icon: "fa-solid fa-database", text: "Basic familiarity with a query language such as SQL is an advantage, not a requirement." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run spreadsheet software, SQL tools, and data visualisation applications." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for cloud-based datasets and dashboarding tools." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Build practical Excel, SQL and Power BI skills",
                "Work with real, business-relevant datasets rather than toy examples",
                "Deliver dashboards and reports that support real decisions",
                "Prepare for data analyst and business intelligence career paths"
            ],
            skills: [
                { icon: "fa-solid fa-file-excel", title: "Advanced Excel", desc: "Formulas, pivot tables and data modelling for real analysis work." },
                { icon: "fa-solid fa-database", title: "SQL for Analysts", desc: "Query, join and aggregate data stored in relational databases." },
                { icon: "fa-solid fa-chart-pie", title: "Power BI Dashboards", desc: "Build interactive dashboards that communicate insight clearly." },
                { icon: "fa-brands fa-python", title: "Python for Data", desc: "Automate data cleaning and analysis with Python libraries." },
                { icon: "fa-solid fa-chart-simple", title: "Data Visualisation", desc: "Turn raw numbers into charts and stories people understand." },
                { icon: "fa-solid fa-briefcase", title: "Business Intelligence", desc: "Connect data analysis to real business questions and decisions." }
            ],
            projects: [
                { title: "Sales Performance Dashboard", desc: "An interactive Power BI dashboard tracking real sales data." },
                { title: "SQL Data Exploration", desc: "Query and analyse a multi-table relational database." },
                { title: "Automated Reporting Tool", desc: "A Python script that cleans and summarises data automatically." },
                { title: "Business Insights Capstone", desc: "A full analysis project presenting insights to a business audience." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-chart-line", title: "Data Analyst" },
                { icon: "fa-solid fa-chart-pie", title: "BI Analyst" },
                { icon: "fa-solid fa-file-lines", title: "Reporting Analyst" },
                { icon: "fa-solid fa-table", title: "Data Coordinator" },
                { icon: "fa-solid fa-lightbulb", title: "Insights Analyst" },
                { icon: "fa-solid fa-briefcase", title: "Junior Business Analyst" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes using real, business-relevant datasets." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Feedback on your dashboards and analysis from working analysts." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified Data Analyst credential on completion." }
            ],
            applyHeading: "Ready to Start Your Analytics Career?",
            applySubtext: "Applications for the next cohort are open now.",
            modes: modes("12 Weeks", {
                hybridFee: "KSh 50,000", hybridStart: "26th October 2026",
                hybridSchedule: "Guided classroom & online sessions | Mon – Fri, 6 PM – 9 PM E.A.T",
                remoteFee: "KSh 50,000", remoteStart: "26th October 2026",
                remoteSchedule: "100% remote classes | Mon – Fri, 6 PM – 9 PM E.A.T",
                ptFee: "KSh 50,000", ptStart: "26th October 2026",
                ptSchedule: "100% remote classes | Mon – Fri, 6 PM – 9 PM E.A.T"
            }),
            faqs: baseFaqs("Data Analytics", "Earn a Germaine-Certified Data Analyst credential on completion.")
        },
        {
            slug: "cloud-computing",
            file: "ai-course-cloud-computing.html",
            category: "cloud-computing",
            categoryLabel: "Cloud Computing",
            eyebrowIcon: "fa-solid fa-cloud",
            title: "Cloud Computing & DevOps",
            titleParts: ["Cloud Computing & ", "DevOps"],
            lead: "Learn Docker, Kubernetes, AWS fundamentals, CI/CD pipelines, Linux administration, automation, and infrastructure deployment.",
            duration: "14 Weeks",
            badgeNumber: "14",
            heroImage: "pics/cloud-network-infrastructure.jpg",
            heroAlt: "Close-up of cloud server network infrastructure and cabling",
            overview: "Modern applications run on cloud infrastructure, and the teams that build and ship them rely on DevOps practices to move fast without breaking things. This programme teaches you to containerise applications, manage infrastructure on AWS, and build automated deployment pipelines — the same practical skills cloud and DevOps engineers use to keep systems running reliably.",
            whoFor: "Contact our admissions team to confirm entry requirements for this programme.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "Open to learners interested in cloud infrastructure and modern IT operations; Intermediate pacing assumes basic computing literacy." }
                ],
                recommended: [
                    { icon: "fa-solid fa-server", text: "Basic familiarity with how servers, networks or websites work is helpful." },
                    { icon: "fa-solid fa-terminal", text: "Some exposure to the command line is an advantage, though it is taught during the programme." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run terminal/command-line tools and connect to cloud platforms." },
                    { icon: "fa-solid fa-wifi", text: "Reliable, reasonably fast internet access for working with cloud-hosted environments." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Build practical Docker, Kubernetes and AWS skills",
                "Practice in real cloud environments, not just theory",
                "Deploy a complete, automated cloud infrastructure project",
                "Prepare for cloud and DevOps engineering career paths"
            ],
            skills: [
                { icon: "fa-brands fa-docker", title: "Docker & Containers", desc: "Package applications so they run consistently anywhere." },
                { icon: "fa-solid fa-dharmachakra", title: "Kubernetes", desc: "Orchestrate and scale containerised applications." },
                { icon: "fa-brands fa-aws", title: "AWS Fundamentals", desc: "Core cloud services for compute, storage and networking." },
                { icon: "fa-solid fa-arrows-spin", title: "CI/CD Pipelines", desc: "Automate testing and deployment from code to production." },
                { icon: "fa-brands fa-linux", title: "Linux Administration", desc: "Manage servers and the command line with confidence." },
                { icon: "fa-solid fa-code-branch", title: "Infrastructure Automation", desc: "Provision and manage infrastructure as code." }
            ],
            projects: [
                { title: "Containerised Web Application", desc: "Package and run a full application using Docker." },
                { title: "Kubernetes Deployment", desc: "Deploy and scale a multi-container application on Kubernetes." },
                { title: "Automated CI/CD Pipeline", desc: "Build a pipeline that tests and deploys code automatically." },
                { title: "Cloud Infrastructure Capstone", desc: "Design and deploy a complete cloud environment on AWS." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-cloud", title: "Cloud Engineer" },
                { icon: "fa-solid fa-arrows-spin", title: "DevOps Engineer" },
                { icon: "fa-solid fa-server", title: "Systems Administrator" },
                { icon: "fa-solid fa-layer-group", title: "Platform Engineer" },
                { icon: "fa-solid fa-gears", title: "Site Reliability Engineer" },
                { icon: "fa-brands fa-aws", title: "AWS Cloud Practitioner" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes with real cloud environments to practice in." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Guidance from working cloud and DevOps engineers." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified Cloud & DevOps credential and preparation for AWS certification." }
            ],
            applyHeading: "Ready to Start Your Cloud Career?",
            applySubtext: "Applications for the next cohort are open now.",
            modes: modes("14 Weeks", {
                hybridFee: "KSh 115,000", hybridStart: "7th September 2026",
                hybridSchedule: "Online & physical lab sessions | Mon – Fri, 6 PM – 9 PM E.A.T",
                remoteFee: "KSh 115,000", remoteStart: "7th September 2026",
                remoteSchedule: "100% online classes | Mon – Fri, 6 PM – 9 PM E.A.T",
                ptFee: "KSh 115,000", ptStart: "7th September 2026",
                ptSchedule: "100% online classes | Mon – Fri, 6 PM – 9 PM E.A.T"
            }),
            faqs: baseFaqs("Cloud Computing & DevOps", "Earn a Germaine-Certified Cloud & DevOps credential and preparation for AWS certification.")
        },
        {
            slug: "python-programming",
            file: "ai-course-python-programming.html",
            category: "python-programming",
            categoryLabel: "Python Programming",
            eyebrowIcon: "fa-brands fa-python",
            title: "Python Programming",
            titleParts: ["Python ", "Programming"],
            lead: "A beginner-friendly bootcamp covering Python fundamentals, automation, APIs, databases, and object-oriented programming.",
            duration: "8 Weeks",
            badgeNumber: "8",
            heroImage: "pics/students-computer-lab.jpg",
            heroAlt: "Students working together at computers in a Germaine lab",
            overview: "Python is one of the most widely used programming languages in the world, powering everything from websites to data science to automation. This programme is built for complete beginners, taking you from your very first line of code through to writing programmes that work with files, APIs and databases — a solid foundation for software development, data or AI paths.",
            whoFor: "No formal prerequisites — this is a beginner-friendly programme built for complete beginners.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "No formal prerequisites — this is a beginner-friendly programme built for complete beginners." }
                ],
                recommended: [
                    { icon: "fa-solid fa-lightbulb", text: "No prior programming experience needed; curiosity and regular practice matter more than background." },
                    { icon: "fa-solid fa-lightbulb", text: "Basic computer literacy (using a keyboard, files and a web browser confidently)." }
                ],
                technical: [
                    { icon: "fa-brands fa-python", text: "A laptop able to install and run Python and a code editor." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for downloading tools and joining live sessions." }
                ]
            },
            level: "Beginner",
            gain: [
                "Build a solid foundation in Python programming",
                "Learn by building real applications, scripts and mini-projects",
                "Work with files, APIs and databases in Python",
                "Prepare for further study in software development, data or AI"
            ],
            skills: [
                { icon: "fa-brands fa-python", title: "Python Fundamentals", desc: "Variables, loops, functions and core programming logic." },
                { icon: "fa-solid fa-cubes", title: "Object-Oriented Programming", desc: "Structure code using classes, objects and reusable components." },
                { icon: "fa-solid fa-gears", title: "Automation Scripting", desc: "Write scripts that handle repetitive tasks automatically." },
                { icon: "fa-solid fa-plug", title: "Working with APIs", desc: "Fetch and use data from external services and applications." },
                { icon: "fa-solid fa-database", title: "Databases with Python", desc: "Store, retrieve and manage data from a Python programme." },
                { icon: "fa-solid fa-bug", title: "Debugging & Testing", desc: "Find and fix errors, and write code you can trust." }
            ],
            projects: [
                { title: "Command-Line Task Manager", desc: "A Python application to add, track and complete tasks." },
                { title: "File Automation Script", desc: "A script that organises and processes files automatically." },
                { title: "API-Powered Mini App", desc: "An application that fetches and displays live data from an API." },
                { title: "Capstone Python Project", desc: "A complete Python application of your own design." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-brands fa-python", title: "Junior Python Developer" },
                { icon: "fa-solid fa-gears", title: "Automation Specialist" },
                { icon: "fa-solid fa-server", title: "Backend Developer" },
                { icon: "fa-solid fa-chart-line", title: "Data Analyst" },
                { icon: "fa-solid fa-screwdriver-wrench", title: "Scripting & Tools Developer" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Beginner-paced classes with plenty of practice time." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Code reviews and guidance from experienced developers." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified Python Programmer credential on completion." }
            ],
            applyHeading: "Ready to Start Learning Python?",
            applySubtext: "Applications for the next cohort are open now.",
            modes: modes("8 Weeks", {
                hybridFee: "KSh 55,000", hybridSchedule: "Guided classroom & online sessions | Mon – Fri, 6 PM – 9 PM E.A.T",
                remoteFee: "KSh 55,000", remoteSchedule: "100% remote classes | Mon – Fri, 6 PM – 9 PM E.A.T",
                ptFee: "KSh 55,000", ptSchedule: "100% remote classes | Mon – Fri, 6 PM – 9 PM E.A.T"
            }),
            faqs: baseFaqs("Python Programming", "Earn a Germaine-Certified Python Programmer credential on completion.", {
                q: "Do I need prior coding experience to join?",
                a: "No. This programme is beginner-friendly and built for complete beginners — no prior coding experience is required."
            })
        },
        {
            slug: "ui-ux-design",
            file: "ai-course-ui-ux-design.html",
            category: "ui-ux-design",
            categoryLabel: "UI/UX Design",
            eyebrowIcon: "fa-solid fa-pen-ruler",
            title: "UI/UX Design",
            titleParts: ["UI", "/UX Design"],
            lead: "Learn user research, wireframing, prototyping, Figma, accessibility, design systems, and responsive interface design.",
            duration: "10 Weeks",
            badgeNumber: "10",
            heroImage: "assets/images/slide/pexels-mikhail-nilov-9301821.jpg",
            heroAlt: "Student sketching a UI/UX wireframe",
            overview: "Good products succeed because they're easy and enjoyable to use, and that starts with thoughtful design. This programme teaches you to understand real users, translate their needs into wireframes and prototypes, and design interfaces that are both beautiful and usable — using the same industry-standard tools and design-system thinking professional product teams rely on.",
            whoFor: "Contact our admissions team to confirm entry requirements for this programme.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "Open to learners with an interest in digital design; Intermediate pacing assumes basic computer literacy and comfort learning new software." }
                ],
                recommended: [
                    { icon: "fa-solid fa-eye", text: "An eye for visual detail and interest in how people interact with apps and websites." },
                    { icon: "fa-brands fa-figma", text: "Prior use of any design or presentation tool (e.g. Canva, PowerPoint, Figma) is an advantage, not a requirement." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run modern design software (e.g. Figma) smoothly." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for cloud-based design collaboration tools." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Build practical user research, wireframing and prototyping skills",
                "Design using the same industry-standard tools professional teams use",
                "Build a complete, reusable design system as a capstone project",
                "Prepare for UI/UX and product design career paths"
            ],
            skills: [
                { icon: "fa-solid fa-magnifying-glass", title: "User Research", desc: "Understand real user needs before you design a single screen." },
                { icon: "fa-solid fa-sitemap", title: "Wireframing", desc: "Sketch and structure interfaces before visual design begins." },
                { icon: "fa-brands fa-figma", title: "Figma Prototyping", desc: "Build interactive, clickable prototypes ready for testing." },
                { icon: "fa-solid fa-universal-access", title: "Accessibility", desc: "Design interfaces that work for people of all abilities." },
                { icon: "fa-solid fa-layer-group", title: "Design Systems", desc: "Build reusable, consistent component libraries." },
                { icon: "fa-solid fa-mobile-screen", title: "Responsive Design", desc: "Design interfaces that adapt cleanly across devices." }
            ],
            projects: [
                { title: "User Research Study", desc: "Interview real users and turn findings into design insights." },
                { title: "Mobile App Prototype", desc: "A clickable Figma prototype for a mobile application." },
                { title: "Website Redesign", desc: "Redesign an existing website with improved usability." },
                { title: "Design System Capstone", desc: "Build a complete, reusable component library and style guide." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-pen-ruler", title: "UI Designer" },
                { icon: "fa-solid fa-users", title: "UX Designer" },
                { icon: "fa-solid fa-magnifying-glass", title: "UX Researcher" },
                { icon: "fa-solid fa-cube", title: "Product Designer" },
                { icon: "fa-solid fa-hand-pointer", title: "Interaction Designer" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes with hands-on design critiques." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Portfolio and design feedback from working designers." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified UI/UX Designer credential on completion." }
            ],
            applyHeading: "Ready to Start Designing?",
            applySubtext: "Applications for the next cohort are open now.",
            modes: modes("10 Weeks", {
                hybridFee: "KSh 145,000", hybridSchedule: "Online & studio sessions | Mon – Fri, 6 PM – 9 PM E.A.T, Sat 9 AM – 1 PM",
                remoteFee: "KSh 145,000", remoteSchedule: "100% online classes | Mon – Fri, 6 PM – 9 PM E.A.T, Sat 9 AM – 1 PM",
                ptFee: "KSh 145,000", ptSchedule: "100% online classes | Mon – Fri, 6 PM – 9 PM E.A.T, Sat 9 AM – 1 PM"
            }),
            faqs: baseFaqs("UI/UX Design", "Earn a Germaine-Certified UI/UX Designer credential on completion.")
        },
        {
            slug: "high-school-bootcamp",
            file: "ai-course-high-school-bootcamp.html",
            category: "high-school-bootcamp",
            categoryLabel: "High School Bootcamp",
            eyebrowIcon: "fa-solid fa-graduation-cap",
            title: "High School Tech Bootcamp",
            titleParts: ["High School ", "Tech Bootcamp"],
            lead: "Introduce students to coding, robotics, AI fundamentals, cybersecurity awareness, digital creativity, and problem-solving.",
            duration: "2–4 Weeks",
            badgeNumber: "4",
            heroImage: "assets/images/slide/pexels-mikhail-nilov-9301899.jpg",
            heroAlt: "High school students in a technology bootcamp session",
            overview: "Designed for school holidays, this bootcamp gives high school students a fun, hands-on first taste of technology — from writing their first lines of code to building simple robots and exploring how AI works. No prior experience is needed. The goal is to build confidence, curiosity and problem-solving skills that carry over into any future study or career path.",
            whoFor: "No prior experience is needed — this holiday bootcamp is designed for high school students new to technology.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "No prior experience is needed — this holiday bootcamp is designed for high school students new to technology." }
                ],
                recommended: [
                    { icon: "fa-solid fa-face-smile", text: "Curiosity about technology and willingness to try new things; no coding background expected." },
                    { icon: "fa-solid fa-lightbulb", text: "Basic computer literacy (using a keyboard and web browser) is helpful." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "Access to a computer during bootcamp sessions — contact admissions for guidance if you need one." }
                ]
            },
            level: "Beginner",
            gain: [
                "Get a fun, hands-on first taste of coding and technology",
                "Build a simple robot and explore how AI works",
                "Build confidence, curiosity and problem-solving skills",
                "Explore future study and career paths in technology"
            ],
            skills: [
                { icon: "fa-solid fa-code", title: "Introduction to Coding", desc: "Write your first programmes and understand how code works." },
                { icon: "fa-solid fa-robot", title: "Robotics Basics", desc: "Build and programme simple robots to complete tasks." },
                { icon: "fa-solid fa-brain", title: "AI Fundamentals", desc: "Understand what AI is and how it's used in everyday life." },
                { icon: "fa-solid fa-shield-halved", title: "Cybersecurity Awareness", desc: "Learn to stay safe online and recognise common threats." },
                { icon: "fa-solid fa-palette", title: "Digital Creativity", desc: "Explore design and creative tools using technology." },
                { icon: "fa-solid fa-puzzle-piece", title: "Problem-Solving", desc: "Build logical thinking through fun, guided challenges." }
            ],
            projects: [
                { title: "First Code Project", desc: "A simple interactive programme built from scratch." },
                { title: "Simple Robot Build", desc: "Assemble and programme a basic robot to complete a task." },
                { title: "Mini AI Demo", desc: "Explore a beginner-friendly AI tool and how it makes decisions." },
                { title: "Showcase Day Project", desc: "Present a project you built to family and fellow students." }
            ],
            careerLabel: "Future Pathways",
            careers: [
                { icon: "fa-solid fa-laptop-code", title: "Software Engineering" },
                { icon: "fa-solid fa-brain", title: "Artificial Intelligence" },
                { icon: "fa-solid fa-shield-halved", title: "Cyber Security" },
                { icon: "fa-solid fa-chart-line", title: "Data Analytics" },
                { icon: "fa-solid fa-pen-ruler", title: "UI/UX Design" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-school", title: "In-Person, On Campus", desc: "Fun, guided sessions in a supervised, safe learning environment." },
                { icon: "fa-solid fa-people-arrows", title: "Friendly Mentors", desc: "Patient, encouraging instructors experienced with young learners." },
                { icon: "fa-solid fa-award", title: "Certificate of Completion", desc: "A certificate to celebrate finishing the holiday bootcamp." }
            ],
            applyHeading: "Ready to Sign Up for the Holidays?",
            applySubtext: "Spaces for the next holiday intake are open now.",
            // High School Bootcamp is holiday/in-person only in all existing source content —
            // kept as a single mode rather than forcing the Full-time/Part-time/Remote template,
            // since inventing remote/hybrid delivery for a supervised on-campus holiday programme
            // for minors would misrepresent how it actually runs.
            modes: [
                {
                    id: "holiday-in-person",
                    label: "Holiday Programme",
                    sub: "In-Person",
                    icon: "fa-solid fa-school",
                    duration: "2–4 Weeks",
                    startDate: "Contact Admissions",
                    fee: "KSh 15,000",
                    schedule: "Supervised, on-campus holiday sessions for high school students."
                }
            ],
            faqs: baseFaqs("High School Tech Bootcamp", "Receive a Certificate of Completion to celebrate finishing the holiday bootcamp.", {
                q: "Do students need any prior experience?",
                a: "No. This bootcamp is designed for complete beginners — no prior experience with coding or technology is needed."
            })
        },
        {
            slug: "data-science",
            file: "ai-course-data-science.html",
            category: "data-analytics",
            categoryLabel: "Data Science",
            eyebrowIcon: "fa-solid fa-database",
            title: "Data Science",
            titleParts: ["Data ", "Science"],
            lead: "Build a rigorous foundation in Python, statistics, machine learning and deep learning, then go further into large language models, fine-tuning and production-ready AI workflows.",
            duration: "31 Weeks",
            badgeNumber: "31",
            heroImage: "pics/students-ai-lab-session.jpg",
            heroAlt: "Students collaborating on a data science project in a lab session",
            overview: "Data Science has moved beyond spreadsheets and charts — today's data specialists are expected to work confidently with AI, not just data. This programme takes you from Python and statistics fundamentals through machine learning, neural networks and large language models, so you leave with the technical depth to build models and the judgement to evaluate AI tools critically rather than trust them blindly.",
            whoFor: "Best suited to university-level students or graduates with some Python or programming familiarity and a quantitative background (basic statistics helps). Admission includes a short technical assessment.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-graduation-cap", text: "Best suited to university-level students or graduates." },
                    { icon: "fa-solid fa-clipboard-check", text: "Admission includes a short technical assessment." }
                ],
                recommended: [
                    { icon: "fa-brands fa-python", text: "Some Python or programming familiarity." },
                    { icon: "fa-solid fa-square-root-variable", text: "A quantitative background — basic statistics helps." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run Python, Jupyter notebooks, and data analysis libraries." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for datasets and cloud-based tools." }
                ]
            },
            level: "Advanced",
            gain: [
                "Build a rigorous foundation in Python, SQL and statistics for data work",
                "Train and evaluate machine learning and deep learning models",
                "Work hands-on with large language models, fine-tuning and prompt engineering",
                "Complete two capstone projects applying AI to real business problems"
            ],
            skills: [
                { icon: "fa-brands fa-python", title: "Python for Data Science", desc: "Control flow, data structures and applied scripting for analysis work." },
                { icon: "fa-solid fa-chart-column", title: "Statistics & Inference", desc: "Hypothesis testing, regression and inferential statistics on real data." },
                { icon: "fa-solid fa-robot", title: "Machine Learning", desc: "Supervised and unsupervised learning with Scikit-Learn." },
                { icon: "fa-solid fa-brain", title: "Neural Networks & Deep Learning", desc: "CNNs, RNNs and transformer-based models for vision and language." },
                { icon: "fa-solid fa-comments", title: "Large Language Models", desc: "Fine-tuning, prompt engineering and responsible LLM deployment." },
                { icon: "fa-solid fa-gears", title: "MLOps Fundamentals", desc: "Experiment tracking, model versioning and reproducible workflows." }
            ],
            projects: [
                { title: "Exploratory Data Analysis Project", desc: "Clean, explore and visualise a real-world dataset end to end." },
                { title: "Predictive Machine Learning Model", desc: "Train and evaluate a classification or regression model on real data." },
                { title: "LLM-Powered Application", desc: "Build an application that integrates a large language model responsibly." },
                { title: "Final Capstone Project", desc: "A complete data science solution combining supervised and AI-assisted analysis." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-chart-line", title: "Data Scientist" },
                { icon: "fa-solid fa-robot", title: "Machine Learning Engineer" },
                { icon: "fa-solid fa-server", title: "Data Engineer" },
                { icon: "fa-solid fa-magnifying-glass-chart", title: "AI Research Analyst" },
                { icon: "fa-solid fa-database", title: "Big Data Analyst" },
                { icon: "fa-solid fa-briefcase", title: "Product Analyst" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes with hands-on lab and project time." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Regular guidance from practising data and AI professionals." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified Data Scientist credential on completion." }
            ],
            applyHeading: "Ready to Build Your Future in Data Science?",
            applySubtext: "Applications for the next cohort are open now.",
            // Data Science mirrors the reference full-time/part-time structure exactly
            // (no separate hybrid pricing tier was published for this programme), so
            // hybrid and full-time remote are priced independently and part-time keeps
            // its own, longer schedule rather than reusing the full-time duration.
            modes: [
                {
                    id: "ft-hybrid", label: "Full-time", sub: "Hybrid", icon: "fa-solid fa-building-user",
                    duration: "31 Weeks", startDate: "31st August 2026", fee: "KSh 195,000",
                    schedule: "3 days remote & 2 days in-person | Mon – Fri, 8 AM – 5 PM E.A.T"
                },
                {
                    id: "ft-remote", label: "Full-time", sub: "Remote", icon: "fa-solid fa-house-laptop",
                    duration: "31 Weeks", startDate: "31st August 2026", fee: "KSh 169,000",
                    schedule: "100% remote classes | Mon – Fri, 8 AM – 5 PM E.A.T"
                },
                {
                    id: "pt-remote", label: "Part-time", sub: "Remote", icon: "fa-solid fa-clock-rotate-left",
                    duration: "50 Weeks", startDate: "31st August 2026", fee: "KSh 195,000",
                    schedule: "100% remote classes | Tue, Wed & Thu, 6 PM – 9 PM E.A.T"
                }
            ],
            faqs: baseFaqs("Data Science", "Earn a Germaine-Certified Data Scientist credential on completion.", {
                q: "How is this different from the Data Analytics programme?",
                a: "Data Analytics focuses on Excel, SQL and Power BI for business reporting. Data Science goes further into Python, machine learning, deep learning and large language models for building predictive and AI-powered systems."
            })
        },
        {
            slug: "intro-cybersecurity",
            file: "ai-course-intro-cybersecurity.html",
            category: "cyber-security",
            categoryLabel: "Cyber Security",
            eyebrowIcon: "fa-solid fa-user-shield",
            title: "Introduction to Cyber Security",
            titleParts: ["Introduction to ", "Cyber Security"],
            lead: "Build a beginner-friendly foundation in networking, cryptography, threat intelligence and incident response — and see how AI is changing modern security practice.",
            duration: "5 Weeks",
            badgeNumber: "5",
            heroImage: "pics/cybersecurity-lock-icon.png",
            heroAlt: "Cyber security lock and network icons displayed over a laptop keyboard",
            overview: "This is a beginner-friendly entry point into cyber security — no prior IT or security background required. You'll build a working foundation across operating systems, networking, cryptography and incident response, while getting a practical look at how AI tools are reshaping day-to-day security work. It's designed as a stepping stone directly into our full Cyber Security programme.",
            whoFor: "Open to complete beginners — high school graduates, university students, and career changers with basic computer literacy and no prior cyber security experience.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-users", text: "Open to complete beginners — high school graduates, university students, and career changers." },
                    { icon: "fa-solid fa-user-check", text: "No prior cyber security experience required." }
                ],
                recommended: [
                    { icon: "fa-solid fa-lightbulb", text: "Basic computer literacy." },
                    { icon: "fa-solid fa-network-wired", text: "An interest in how digital systems and networks work." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run basic security tools and lab exercises used in the programme." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for lab environments and live sessions." }
                ]
            },
            level: "Beginner",
            gain: [
                "Build a working foundation across networking, OS and cryptography basics",
                "Understand core threat intelligence and incident response concepts",
                "See how AI tools are used in day-to-day security work",
                "Prepare to progress directly into the full Cyber Security programme"
            ],
            skills: [
                { icon: "fa-solid fa-shield-halved", title: "Cyber Security Fundamentals", desc: "Core concepts, the CIA triad, and common threat types." },
                { icon: "fa-solid fa-desktop", title: "Operating Systems & Security", desc: "Windows and Linux basics with an eye on how each is secured." },
                { icon: "fa-solid fa-network-wired", title: "Networking Fundamentals", desc: "TCP/IP, the OSI model and basic traffic analysis." },
                { icon: "fa-solid fa-key", title: "Cryptography Basics", desc: "Encryption, hashing, digital signatures and certificates." }
            ],
            projects: [
                { title: "Threat Landscape Briefing", desc: "Research and present common threats facing a real organisation type." },
                { title: "Network Traffic Walkthrough", desc: "Use packet-analysis tools to inspect and interpret sample traffic." },
                { title: "Security Awareness Guide", desc: "Produce a short guide teaching non-technical staff safe practices." }
            ],
            careerLabel: "Where It Can Lead",
            careers: [
                { icon: "fa-solid fa-headset", title: "IT Support Specialist" },
                { icon: "fa-solid fa-network-wired", title: "Network Administrator" },
                { icon: "fa-solid fa-magnifying-glass", title: "Threat Intelligence Analyst (Junior)" },
                { icon: "fa-solid fa-shield-halved", title: "Cyber Security Intern" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes built for complete beginners." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Guidance from working security professionals." },
                { icon: "fa-solid fa-award", title: "Certificate of Completion", desc: "A certificate recognising your foundation in cyber security." }
            ],
            applyHeading: "Ready to Start Your Cyber Security Journey?",
            applySubtext: "Applications for the next cohort are open now.",
            // Introduction to Cyber Security is published with two remote tracks only —
            // no hybrid/on-campus option exists for this short foundation course, so it
            // is not forced into the standard three-mode template.
            modes: [
                {
                    id: "ft-remote", label: "Full-time", sub: "Remote", icon: "fa-solid fa-house-laptop",
                    duration: "5 Weeks", startDate: "28th September 2026", fee: "KSh 35,000",
                    schedule: "100% remote classes | Mon – Fri, 8 AM – 5 PM E.A.T"
                },
                {
                    id: "pt-remote", label: "Part-time", sub: "Remote", icon: "fa-solid fa-clock-rotate-left",
                    duration: "11 Weeks", startDate: "28th September 2026", fee: "KSh 35,000",
                    schedule: "100% remote classes | Mon – Fri, 6 PM – 9 PM E.A.T"
                }
            ],
            faqs: baseFaqs("Introduction to Cyber Security", "Receive a Certificate of Completion and be ready to progress into the full Cyber Security programme.", {
                q: "Can I go straight into the full Cyber Security Bootcamp instead?",
                a: "The full Cyber Security programme assumes some foundational knowledge. If you're new to the field, this introductory course is the recommended starting point."
            })
        },
        {
            slug: "intro-devops",
            file: "ai-course-intro-devops.html",
            category: "cloud-computing",
            categoryLabel: "Cloud Computing & DevOps",
            eyebrowIcon: "fa-solid fa-server",
            title: "Introduction to DevOps Engineering",
            titleParts: ["Introduction to ", "DevOps Engineering"],
            lead: "Learn the practices behind modern software delivery — CI/CD pipelines, cloud infrastructure, Infrastructure as Code, and containerisation — through hands-on labs.",
            duration: "10 Weeks",
            badgeNumber: "10",
            heroImage: "pics/server-rack-cabling.jpg",
            heroAlt: "Close-up of a technician connecting server rack network cabling",
            overview: "DevOps combines software development and IT operations to help teams ship reliable software faster. This programme is built for developers and IT professionals ready to move into cloud and automation roles — covering CI/CD pipelines, Infrastructure as Code, containers and Kubernetes fundamentals through hands-on labs and real deployment scenarios, not just theory.",
            whoFor: "Best suited to software engineers or IT professionals with some backend or full-stack development background, comfortable with Git workflows and basic command-line use.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-user-check", text: "Best suited to software engineers or IT professionals with some backend or full-stack development background." }
                ],
                recommended: [
                    { icon: "fa-brands fa-git-alt", text: "Comfortable with Git workflows." },
                    { icon: "fa-solid fa-terminal", text: "Basic command-line use." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop able to run Git, a terminal, and the automation/containerisation tools used in the programme." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access for cloud and CI/CD tooling." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Understand core DevOps culture, workflows and the CI/CD pipeline",
                "Provision and manage infrastructure using Infrastructure as Code",
                "Containerise applications and deploy them with Kubernetes fundamentals",
                "Build a portfolio of hands-on DevOps automation projects"
            ],
            skills: [
                { icon: "fa-solid fa-code-branch", title: "CI/CD Pipelines", desc: "Automated builds, testing and deployment with modern CI tools." },
                { icon: "fa-solid fa-file-code", title: "Infrastructure as Code", desc: "Provision cloud infrastructure with Terraform and Ansible." },
                { icon: "fa-solid fa-linux", title: "Linux & Systems Fundamentals", desc: "Command-line administration, permissions and system monitoring." },
                { icon: "fa-solid fa-box", title: "Containers & Kubernetes", desc: "Docker fundamentals and deploying workloads to Kubernetes." }
            ],
            projects: [
                { title: "CI/CD Pipeline Build", desc: "Configure an automated build-and-deploy pipeline for a sample app." },
                { title: "Infrastructure as Code Project", desc: "Provision cloud infrastructure using Terraform from scratch." },
                { title: "Containerised Deployment Capstone", desc: "Package and deploy an application on Kubernetes end to end." }
            ],
            careerLabel: "Career Opportunities",
            careers: [
                { icon: "fa-solid fa-server", title: "DevOps Engineer (Junior)" },
                { icon: "fa-solid fa-cloud-arrow-up", title: "Cloud Engineer" },
                { icon: "fa-solid fa-code-branch", title: "CI/CD Engineer" },
                { icon: "fa-solid fa-gears", title: "Automation Engineer" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes with hands-on infrastructure labs." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Guidance from a working DevOps engineer." },
                { icon: "fa-solid fa-award", title: "Certification", desc: "Earn a Germaine-Certified DevOps Fundamentals credential on completion." }
            ],
            applyHeading: "Ready to Start Your DevOps Journey?",
            applySubtext: "Applications for the next cohort are open now.",
            // Introduction to DevOps Engineering is published as a single part-time
            // remote track — no hybrid or full-time option exists for this course.
            modes: [
                {
                    id: "pt-remote", label: "Part-time", sub: "Remote", icon: "fa-solid fa-clock-rotate-left",
                    duration: "10 Weeks", startDate: "7th September 2026", fee: "KSh 50,000",
                    schedule: "100% remote classes | Mon – Fri, 6 PM – 9 PM E.A.T"
                }
            ],
            faqs: baseFaqs("Introduction to DevOps Engineering", "Earn a Germaine-Certified DevOps Fundamentals credential on completion.")
        },
        {
            slug: "generative-ai-essentials",
            file: "ai-course-generative-ai-essentials.html",
            category: "ai-for-business",
            categoryLabel: "AI for Business",
            eyebrowIcon: "fa-solid fa-wand-magic-sparkles",
            title: "Generative AI Essentials",
            titleParts: ["Generative AI ", "Essentials"],
            lead: "A fast-paced, non-technical course that teaches working professionals to use generative AI for writing, research, presentations and data insight.",
            duration: "2 Weeks",
            badgeNumber: "2",
            heroImage: "pics/professional-ai-business.jpg",
            heroAlt: "A working professional using AI tools at a laptop in a modern office",
            overview: "Generative AI is now part of everyday work, whether you're in marketing, operations, HR or leadership. This short, hands-on course teaches you practical prompt engineering, document and data workflows, and responsible AI use — no technical background needed. You'll leave able to use AI assistants confidently and productively in your own role.",
            whoFor: "Designed for working professionals and enthusiastic learners with basic computer literacy — no coding or prior AI experience required.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-briefcase", text: "Designed for working professionals and enthusiastic learners." },
                    { icon: "fa-solid fa-user-check", text: "No coding or prior AI experience required." }
                ],
                recommended: [
                    { icon: "fa-solid fa-lightbulb", text: "Basic computer literacy." },
                    { icon: "fa-solid fa-wand-magic-sparkles", text: "An interest in applying AI tools to everyday or workplace tasks." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop or computer with a modern web browser for accessing the AI tools used in the programme." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access, since most tools covered are cloud-based." }
                ]
            },
            level: "Beginner",
            gain: [
                "Write effective prompts using proven prompt-engineering techniques",
                "Use generative AI for document analysis, planning and reporting",
                "Create presentations and visual summaries with AI assistance",
                "Apply responsible-AI principles to everyday workplace use"
            ],
            skills: [
                { icon: "fa-solid fa-comments", title: "Prompt Engineering", desc: "Zero-shot, few-shot and chain-of-thought prompting techniques." },
                { icon: "fa-solid fa-file-lines", title: "AI-Assisted Productivity", desc: "Document analysis, summarising and workplace automation basics." },
                { icon: "fa-solid fa-chart-simple", title: "AI-Powered Data Insight", desc: "Using AI to analyse spreadsheets and surface faster insights." },
                { icon: "fa-solid fa-scale-balanced", title: "Responsible AI Use", desc: "Data privacy, accuracy checks and ethical use of AI tools." }
            ],
            projects: [
                { title: "AI-Assisted Report", desc: "Produce a polished workplace report using AI drafting and editing." },
                { title: "AI-Generated Presentation", desc: "Build a structured slide deck using AI presentation tools." },
                { title: "Personal AI Workflow Project", desc: "Design an AI-assisted workflow for a task from your own role." }
            ],
            careerLabel: "Who This Helps",
            careers: [
                { icon: "fa-solid fa-bullhorn", title: "Marketing & Content Professionals" },
                { icon: "fa-solid fa-briefcase", title: "Business Leaders & Managers" },
                { icon: "fa-solid fa-users", title: "Operations & Admin Teams" },
                { icon: "fa-solid fa-lightbulb", title: "Entrepreneurs & Freelancers" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live Online Workshops", desc: "Practical, hands-on sessions with recordings available for review." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Guidance from instructors experienced in applied AI use." },
                { icon: "fa-solid fa-award", title: "Certificate of Completion", desc: "A certificate recognising your Generative AI Essentials training." }
            ],
            applyHeading: "Ready to Future-Proof Your Career?",
            applySubtext: "Spaces for the next intake are open now.",
            // Generative AI Essentials is a single short part-time remote course —
            // no other learning mode is published for this format.
            modes: [
                {
                    id: "pt-remote", label: "Part-time", sub: "Remote", icon: "fa-solid fa-clock-rotate-left",
                    duration: "2 Weeks", startDate: "Contact Admissions", fee: "KSh 20,000",
                    schedule: "100% remote live sessions | Twice weekly evening classes"
                }
            ],
            faqs: baseFaqs("Generative AI Essentials", "Receive a Certificate of Completion recognising your Generative AI Essentials training.")
        },
        {
            slug: "ai-agents-automation",
            file: "ai-course-ai-agents-automation.html",
            category: "ai-for-business",
            categoryLabel: "AI for Business",
            eyebrowIcon: "fa-solid fa-gears",
            title: "AI Agents & Workflow Automation",
            titleParts: ["AI Agents & ", "Workflow Automation"],
            lead: "Design and build smart, no-code workflows and AI-powered agents that automate real business tasks — no coding background required.",
            duration: "3 Weeks",
            badgeNumber: "3",
            heroImage: "assets/images/slide/pexels-mohammad-yasir-3365802-5198392.jpg",
            heroAlt: "Close-up of automated data workflows on a screen",
            overview: "Workflow automation and AI agents are becoming essential business skills, not futuristic ones. This course takes you from the basics of no-code automation tools through to designing AI agents that draft content, process data and support multi-step business tasks — balancing practical projects with plain-language concepts so you can apply what you learn immediately.",
            whoFor: "Open to professionals, entrepreneurs and operations teams with basic computer literacy — no coding background is required.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-briefcase", text: "Open to professionals, entrepreneurs and operations teams." },
                    { icon: "fa-solid fa-user-check", text: "No coding background is required." }
                ],
                recommended: [
                    { icon: "fa-solid fa-lightbulb", text: "Basic computer literacy." },
                    { icon: "fa-solid fa-diagram-project", text: "An interest in streamlining repetitive tasks or workflows." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop or computer with a modern web browser for accessing the automation platforms used in the programme." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access, since most tools covered are cloud-based." }
                ]
            },
            level: "Beginner",
            gain: [
                "Build no-code automated workflows connecting everyday business apps",
                "Design and deploy simple AI agents for content and data tasks",
                "Add human-in-the-loop approval steps to automated processes",
                "Walk away with a portfolio-ready automation project"
            ],
            skills: [
                { icon: "fa-solid fa-diagram-project", title: "No-Code Workflow Design", desc: "Build automations connecting apps like Sheets, Slack and email." },
                { icon: "fa-solid fa-robot", title: "AI Agent Basics", desc: "Design simple AI agents for content generation and classification." },
                { icon: "fa-solid fa-database", title: "Spreadsheet & Database Automation", desc: "Automate reading and writing data across common tools." },
                { icon: "fa-solid fa-triangle-exclamation", title: "Error Handling & Monitoring", desc: "Spot and troubleshoot common workflow failures." }
            ],
            projects: [
                { title: "First Automated Workflow", desc: "Connect two everyday apps into a working no-code automation." },
                { title: "Content-Generating AI Agent", desc: "Build an agent that drafts emails, posts or summaries automatically." },
                { title: "Business Automation Capstone", desc: "Design a complete AI-powered automation for a real business task." }
            ],
            careerLabel: "Who This Helps",
            careers: [
                { icon: "fa-solid fa-briefcase", title: "Operations & Admin Professionals" },
                { icon: "fa-solid fa-bullhorn", title: "Marketers & Content Creators" },
                { icon: "fa-solid fa-user-tie", title: "Entrepreneurs & Consultants" },
                { icon: "fa-solid fa-gears", title: "Junior Automation Specialists" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Hands-on, project-based sessions with practising instructors." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Guidance from practitioners in AI and automation." },
                { icon: "fa-solid fa-award", title: "Certificate of Completion", desc: "A certificate recognising your AI automation training." }
            ],
            applyHeading: "Ready to Start Automating?",
            applySubtext: "Applications for the next cohort are open now.",
            // AI Agents & Workflow Automation is published with two remote tracks only —
            // no hybrid/on-campus option exists for this course.
            modes: [
                {
                    id: "ft-remote", label: "Full-time", sub: "Remote", icon: "fa-solid fa-house-laptop",
                    duration: "3 Weeks", startDate: "28th September 2026", fee: "KSh 35,000",
                    schedule: "100% online classes | Mon – Fri, 8 AM – 5 PM E.A.T"
                },
                {
                    id: "pt-remote", label: "Part-time", sub: "Remote", icon: "fa-solid fa-clock-rotate-left",
                    duration: "10 Weeks", startDate: "28th September 2026", fee: "KSh 50,000",
                    schedule: "100% online classes | Mon & Wed, 6 PM – 8:30 PM E.A.T"
                }
            ],
            faqs: baseFaqs("AI Agents & Workflow Automation", "Receive a Certificate of Completion recognising your AI automation training.")
        },
        {
            slug: "digital-marketing-ai",
            file: "ai-course-digital-marketing-ai.html",
            category: "ai-for-business",
            categoryLabel: "AI for Business",
            eyebrowIcon: "fa-solid fa-bullhorn",
            title: "Digital Marketing with AI",
            titleParts: ["Digital Marketing ", "with AI"],
            lead: "Master modern digital marketing — strategy, content, SEO, performance campaigns and analytics — accelerated by today's leading AI tools.",
            duration: "4 Weeks",
            badgeNumber: "4",
            heroImage: "assets/images/slide/working.jpg",
            heroAlt: "Marketing professionals presenting in a boardroom",
            overview: "AI is changing how marketers research, create, optimise and measure campaigns. This course combines proven digital marketing fundamentals — strategy, content, SEO and performance marketing — with practical AI workflows, so you can build campaigns faster, uncover audience insights instantly, and automate the repetitive parts of the job.",
            whoFor: "Best suited to marketers, brand managers, entrepreneurs and business owners with working knowledge of at least one digital marketing channel.",
            requirements: {
                entry: [
                    { icon: "fa-solid fa-bullhorn", text: "Best suited to marketers, brand managers, entrepreneurs and business owners." }
                ],
                recommended: [
                    { icon: "fa-solid fa-lightbulb", text: "Working knowledge of at least one digital marketing channel (e.g. social media, email, or search)." },
                    { icon: "fa-solid fa-lightbulb", text: "Comfort using online tools and platforms in a work context." }
                ],
                technical: [
                    { icon: "fa-solid fa-laptop", text: "A laptop or computer with a modern web browser for accessing the AI and marketing tools used in the programme." },
                    { icon: "fa-solid fa-wifi", text: "Reliable internet access, since most tools covered are cloud-based." }
                ]
            },
            level: "Intermediate",
            gain: [
                "Build AI-powered digital marketing strategies and campaigns",
                "Create content, visuals and copy faster using AI tools",
                "Improve search and social visibility with AI-assisted SEO",
                "Turn campaign data into decisions using AI-powered analytics"
            ],
            skills: [
                { icon: "fa-solid fa-bullseye", title: "AI-Powered Strategy", desc: "Audience research, personas and campaign planning with AI support." },
                { icon: "fa-solid fa-pen-nib", title: "AI Content Creation", desc: "Produce content and visual assets faster using AI tools." },
                { icon: "fa-solid fa-magnifying-glass", title: "SEO & AI Search Visibility", desc: "Improve visibility across search engines and AI-powered platforms." },
                { icon: "fa-solid fa-chart-line", title: "AI-Powered Analytics", desc: "Turn marketing data into actionable insight and reporting." }
            ],
            projects: [
                { title: "AI-Assisted Campaign Strategy", desc: "Build a complete marketing strategy using AI research tools." },
                { title: "Content & Visual Asset Sprint", desc: "Produce a set of campaign-ready content and visuals with AI." },
                { title: "Integrated Campaign Capstone", desc: "Launch a complete AI-powered marketing campaign end to end." }
            ],
            careerLabel: "Who This Helps",
            careers: [
                { icon: "fa-solid fa-bullhorn", title: "Digital Marketing Specialist" },
                { icon: "fa-solid fa-chart-line", title: "Growth Marketer" },
                { icon: "fa-solid fa-briefcase", title: "Brand & Product Marketing Manager" },
                { icon: "fa-solid fa-user-tie", title: "Marketing Consultant / Freelancer" }
            ],
            formatLabel: "Learning Format",
            format: [
                { icon: "fa-solid fa-chalkboard-user", title: "Live, Guided Sessions", desc: "Instructor-led classes with practical marketing labs." },
                { icon: "fa-solid fa-people-arrows", title: "Mentor Support", desc: "Guidance from a working digital marketing practitioner." },
                { icon: "fa-solid fa-award", title: "Certificate of Completion", desc: "A certificate recognising your Digital Marketing with AI training." }
            ],
            applyHeading: "Ready to Become an AI-Powered Marketer?",
            applySubtext: "Applications for the next cohort are open now.",
            // Digital Marketing with AI is published as a single part-time remote
            // course — no other learning mode exists for this format.
            modes: [
                {
                    id: "pt-remote", label: "Part-time", sub: "Remote", icon: "fa-solid fa-clock-rotate-left",
                    duration: "4 Weeks", startDate: "Contact Admissions", fee: "KSh 50,000",
                    schedule: "100% online classes | Tue & Thu, 6 PM – 8:30 PM E.A.T"
                }
            ],
            faqs: baseFaqs("Digital Marketing with AI", "Receive a Certificate of Completion recognising your Digital Marketing with AI training.")
        }
    ];

    var CATEGORIES = [
        { id: "all", label: "All Programmes", icon: "fa-solid fa-layer-group" },
        { id: "ai", label: "Artificial Intelligence", icon: "fa-solid fa-brain" },
        { id: "software-engineering", label: "Software Engineering", icon: "fa-solid fa-code" },
        { id: "cyber-security", label: "Cyber Security", icon: "fa-solid fa-shield-halved" },
        { id: "data-analytics", label: "Data Analytics", icon: "fa-solid fa-chart-line" },
        { id: "cloud-computing", label: "Cloud Computing", icon: "fa-solid fa-cloud" },
        { id: "python-programming", label: "Python Programming", icon: "fa-brands fa-python" },
        { id: "ui-ux-design", label: "UI/UX Design", icon: "fa-solid fa-pen-ruler" },
        { id: "ai-for-business", label: "AI for Business", icon: "fa-solid fa-briefcase" },
        { id: "high-school-bootcamp", label: "High School Bootcamp", icon: "fa-solid fa-graduation-cap" }
    ];

    function getCourseBySlug(slug) {
        for (var i = 0; i < COURSES.length; i++) {
            if (COURSES[i].slug === slug) return COURSES[i];
        }
        return null;
    }

    function getCourseByFile(filename) {
        for (var i = 0; i < COURSES.length; i++) {
            if (COURSES[i].file === filename) return COURSES[i];
        }
        return null;
    }

    global.GermaineAICourses = {
        courses: COURSES,
        categories: CATEGORIES,
        getBySlug: getCourseBySlug,
        getByFile: getCourseByFile
    };

})(window);
