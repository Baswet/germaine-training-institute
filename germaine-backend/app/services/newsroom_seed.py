"""
Launch content for the News & Events publication (researched 21–22 Nov 2026).

Every story was checked against the original publisher's article; the
summaries below are original wording and each story credits and links its
source. Politics is excluded by editorial decision. No images are bundled
(the page uses generated category artwork), no reads are invented, nothing
is marked Breaking, and no video is listed until an editor adds one from a
publisher's official channel.

Idempotent: stories are matched on their original URL and events on their
slug, so running it twice creates nothing new. Existing rows are left
untouched (editors may have changed them since).
"""

from datetime import date, datetime, timedelta, timezone

from app.extensions import db
from app.models import NewsArticle
from app.models.newsroom import NEWS_CATEGORY_LABELS, NewsArticleMeta, NewsEvent
from app.services import cms_service

EAT = timezone(timedelta(hours=3))


def _t(y, m, d, hh=0, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=EAT).astimezone(timezone.utc)


STORIES = [
    dict(
        title="Kenya begins rolling out 10.8 million mosquito nets across 18 counties",
        summary="The Ministry of Health has started distributing more than 10.7 million insecticide-treated "
                "nets in 18 malaria-endemic counties, covering 99 sub-counties, in a campaign that began on 19 November.",
        body="Distribution of 10,791,601 long-lasting insecticidal nets started on 19 November.\n"
             "The campaign targets 99 sub-counties in 18 counties where malaria is endemic.\n"
             "Households are advised to follow guidance from local health officials on collection points.",
        news_category="kenya", source_name="Citizen Digital",
        source_url="https://citizen.digital/article/govt-to-distribute-107m-mosquito-nets-across-18-malaria-endemic-counties-n394197",
        source_published_at=_t(2026, 11, 19, 5, 8),
        is_featured=True, feature_rank=80, is_trending=True,
        trending_note="Covered by several Kenyan outlets",
    ),
    dict(
        title="UK unveils Ksh6.8 billion 'Forge Africa' push to help Kenyan firms attract investors",
        summary="The UK has announced a Ksh6.8 billion initiative, Forge Africa, aimed at helping Kenyan businesses "
                "become investment-ready and connect with investors. It was announced on 19 November by the UK Minister for Africa.",
        news_category="business", source_name="Kenyans.co.ke",
        source_url="https://www.kenyans.co.ke/news/129549-uk-launches-ksh68-billion-initiative-help-kenyan-businesses-attract-investors",
        source_published_at=_t(2026, 11, 20, 14, 21),
    ),
    dict(
        title="KCB Group nine-month profit climbs 24% to Sh58.6 billion",
        summary="KCB Group reported a 23.9 percent rise in profit for the nine months of 2026, reaching Sh58.6 billion.",
        news_category="business", source_name="Capital FM",
        source_url="https://capitalfm.africa/kcb-group-nine-month-profit-rises-24pc-to-sh58-6bn/",
        source_published_at=_t(2026, 11, 18, 12, 0),
        is_trending=True, trending_note="Widely reported business result",
    ),
    dict(
        title="Turkana oil: rig activation set for 20 November, first production targeted for 1 December",
        summary="Energy and Petroleum CS Opiyo Wandayi has set out a timeline for the Turkana oil project, with rig "
                "activation scheduled for 20 November and first oil production targeted for 1 December 2026, ahead of exports.",
        body="The timeline was outlined on 18 November.\n"
             "Rig activation was scheduled for 20 November 2026.\n"
             "First production is targeted for 1 December 2026, ahead of planned exports.",
        news_category="business", source_name="The Kenya Times",
        source_url="https://thekenyatimes.com/business/kenya-sets-timeline-for-turkana-oil-production-ahead-of-first-exports/",
        source_published_at=_t(2026, 11, 19, 9, 0),
        is_featured=True, feature_rank=100, is_trending=True,
        trending_note="Major national economic story",
    ),
    dict(
        title="Harambee Stars fall 2-1 to South Africa at Nyayo Stadium",
        summary="Kenya lost 2-1 to South Africa in an AFCON 2027 qualifier at Nyayo Stadium on 17 November, with "
                "Mofokeng scoring twice. Kenya has already qualified for AFCON 2027 as a co-host.",
        news_category="sports", source_name="Nation",
        source_url="https://nation.africa/kenya/sports/football/harambee-stars-fall-to-bafana-bafana-in-hard-fought-contest-5674466",
        source_published_at=_t(2026, 11, 17, 21, 0),
        is_featured=True, feature_rank=90, is_trending=True,
        trending_note="Reported by Nation, Citizen Digital and The Standard",
    ),
    dict(
        title="Olunga calls on FKF to 'put its house in order'",
        summary="Harambee Stars captain Michael Olunga has publicly urged the Football Kenya Federation to sort out "
                "its affairs, following the team's recent qualifier.",
        news_category="sports", source_name="Capital FM",
        source_url="https://capitalfm.africa/put-your-house-in-order-harambee-stars-skipper-reads-riot-act-to-fkf/",
        source_published_at=_t(2026, 11, 18, 12, 0),
    ),
    dict(
        title="Felix Kipkoech wins the Incheon Marathon in 2:09:42",
        summary="Kenyan runner Felix Kipkoech won the Incheon Marathon in South Korea, finishing in 2 hours 9 minutes 42 seconds.",
        news_category="sports", source_name="The Kenya Times",
        source_url="https://thekenyatimes.com/sports/felix-kipkoech-in-korea/",
        source_published_at=_t(2026, 11, 22, 9, 0),
        is_editors_pick=True,
    ),
    dict(
        title="Berlin collective Keinemusik lands in Kenya ahead of Uhuru Gardens show",
        summary="The Berlin-based DJ collective Keinemusik has arrived in Kenya ahead of its weekend concert at "
                "Uhuru Gardens on 21 November.",
        news_category="entertainment", source_name="KBC",
        source_url="https://www.kbc.co.ke/berlin-collective-keinemusic-lands-in-kenya-ahead-of-weekend-concert/",
        source_published_at=_t(2026, 11, 20, 12, 0),
        is_featured=True, feature_rank=40,
    ),
    dict(
        title="M-PESA raises capacity to 6,000 transactions per second",
        summary="Safaricom has increased M-PESA's processing capacity from 4,500 to 6,000 transactions per second. "
                "The platform handled 46 billion transactions worth Ksh41.7 trillion in the year to March 2026.",
        news_category="technology", source_name="People Daily",
        source_url="https://peopledaily.digital/business/m-pesa-raises-processing-capacity-to-6000-transactions-per-second-as-volumes-hit-46b",
        source_published_at=_t(2026, 11, 20, 12, 30),
        is_featured=True, feature_rank=50,
    ),
    dict(
        title="Man charged over alleged Ksh4.9 million fraud posing as Mombasa lands director",
        summary="A man has been charged at the Shanzu Law Courts over an alleged Ksh4.9 million fraud in which he is "
                "accused of posing as a Mombasa lands director. The charges are allegations that have not been proven in court.",
        news_category="crime", source_name="Kenyans.co.ke",
        source_url="https://www.kenyans.co.ke/news/129557-man-charged-allegedly-posing-mombasa-lands-director-ksh49-million-fraud",
        source_published_at=_t(2026, 11, 20, 17, 27),
    ),
    dict(
        title="DCI arrests suspect in deputy OCS murder after nearly three years",
        summary="Detectives have arrested a suspect sought in connection with the killing of a deputy OCS in Rumuruti, "
                "nearly three years after the incident. The suspect has not been convicted.",
        news_category="crime", source_name="Kenyans.co.ke",
        source_url="https://www.kenyans.co.ke/news/129394-dci-arrests-deputy-ocs-murder-suspect-after-nearly-3-years-run",
        source_published_at=_t(2026, 11, 15, 11, 39),
    ),
    dict(
        title="High Court declines to stop DCI probe of lawyer in Sh5m land dispute",
        summary="The High Court has declined a request to bar the DCI from investigating a lawyer over a Sh5 million "
                "land dispute. No finding of wrongdoing has been made.",
        news_category="crime", source_name="The Standard",
        source_url="https://www.standardmedia.co.ke/crime-and-justice/article/2001562457/court-declines-to-bar-dci-from-arresting-lawyer-in-sh5m-land-dispute",
        source_published_at=_t(2026, 11, 17, 12, 0),
    ),
    dict(
        title="Kenya's last Ebola patient discharged as 42-day countdown begins",
        summary="The World Health Organization reports that Kenya's last Ebola patient went home on 11 November, "
                "starting a 42-day countdown. If no new cases are confirmed, Kenya could be declared Ebola-free on 23 December.",
        news_category="lifestyle", source_name="WHO Africa",
        source_url="https://www.afro.who.int/countries/kenya/news/kenyas-last-ebola-patient-goes-home-42-day-countdown-begins",
        source_published_at=_t(2026, 11, 11, 12, 0),
        is_trending=True, trending_note="Public health milestone",
    ),
    dict(
        title="Editors urged to step up coverage of maternal and newborn health",
        summary="Kenyan media editors have been encouraged to give more coverage to maternal and newborn health issues.",
        news_category="lifestyle", source_name="KBC",
        source_url="https://kbc.co.ke/kenyan-media-urged-to-step-up-coverage-of-maternal-and-newborn-health",
        source_published_at=_t(2026, 11, 20, 12, 0),
    ),
    dict(
        title="Technical training to be more accessible through student-centred funding",
        summary="Technical and vocational training is set to become more accessible through the student-centred funding "
                "model. KNBS data shows TVET enrolment rose 17.3 percent to 825,484 trainees in 2025.",
        news_category="education", source_name="Kenya News Agency",
        source_url="https://www.kenyanews.go.ke/technical-trainings-to-be-accessible-through-student-centered-funding/",
        source_published_at=_t(2026, 11, 21, 12, 0),
    ),
    dict(
        title="Eight Kenyan students flagged off for Huawei's Seeds for the Future programme",
        summary="Eight Kenyan students have been flagged off to take part in Huawei's global Seeds for the Future ICT programme.",
        news_category="education", source_name="KBC",
        source_url="https://kbc.co.ke/kenya-flags-off-8-students-for-huaweis-global-ict-programme",
        source_published_at=_t(2026, 11, 20, 12, 0),
        is_editors_pick=True,
    ),
    dict(
        title="Kenyan journalists among winners at the IGAD Media Awards in Kampala",
        summary="Kenyan journalists, including Jamila Mohamed and Angela Kezengwa, were among the winners at the IGAD "
                "Media Awards held in Kampala on 20 November.",
        news_category="world", source_name="Citizen Digital",
        source_url="https://citizen.digital/article/rms-journalist-angela-kezengwa-feted-at-the-igad-media-award-n394298",
        source_published_at=_t(2026, 11, 21, 9, 38),
        is_editors_pick=True,
    ),
]

EVENTS = [
    dict(slug="wfcp-world-congress-2026", title="WFCP World Congress 2026", category="conference",
         description="The World Federation of Colleges and Polytechnics' global congress on technical and vocational "
                     "education, hosted in Nairobi with ATUPA.",
         organizer="World Federation of Colleges and Polytechnics (WFCP) & ATUPA",
         start_date=date(2026, 11, 23), end_date=date(2026, 11, 26), venue="KICC", county="Nairobi",
         source_url="https://wfcp.org/our-work/world-congress/upcoming-congress/", is_featured=True),
    dict(slug="women-in-tech-summit-kenya-2026", title="Women In Tech Summit Kenya 2026", category="technology",
         description="The second edition of the Women In Tech Summit Kenya, bringing together women working in technology.",
         organizer="Tambua Women in Tech", start_date=date(2026, 11, 27), end_date=date(2026, 11, 28),
         county="Nairobi", source_url="https://pretalx.com/witsummitkenya/cfp"),
    dict(slug="wordcamp-nairobi-2026", title="WordCamp Nairobi 2026", category="technology",
         description="A community conference for people who use and build with WordPress.",
         organizer="WordPress Nairobi community", start_date=date(2026, 11, 27), end_date=date(2026, 11, 28),
         start_time="9:00 AM – 5:00 PM", venue="ALX Tech Hub, The Piano, Westlands", county="Nairobi",
         source_url="https://nairobi.wordcamp.org", registration_url="https://nairobi.wordcamp.org/2026/tickets/"),
    dict(slug="devfest-pwani-2026", title="DevFest Pwani 2026", category="technology",
         description="A developer festival run by the Google Developer Group in Pwani.",
         organizer="GDG Pwani", start_date=date(2026, 11, 28), county="Mombasa",
         source_url="https://sessionize.com/devfest-pwani-2026/"),
    dict(slug="kenya-expo-2026", title="20th Kenya Expo 2026", category="exhibition",
         description="The 20th edition of the Kenya Expo trade exhibition.",
         organizer="Inexpo Group", start_date=date(2026, 11, 19), end_date=date(2026, 11, 22), venue="KICC",
         county="Nairobi", source_url="https://businessradar.co.ke/kenya-business-events/kenya-expo-2026/"),
    dict(slug="the-nutcracker-2026", title="The Nutcracker 2026", category="culture",
         description="Dance Centre Kenya's seasonal ballet production of The Nutcracker.",
         organizer="Dance Centre Kenya", start_date=date(2026, 11, 20), end_date=date(2026, 11, 22),
         date_note="Further shows on 28–29 November", venue="Kenya National Theatre", county="Nairobi",
         source_url="https://kenyabuzz.com/events"),
    dict(slug="the-nutcracker-2026-second-weekend", title="The Nutcracker 2026 (second weekend)", category="culture",
         description="Second weekend of Dance Centre Kenya's production of The Nutcracker.",
         organizer="Dance Centre Kenya", start_date=date(2026, 11, 28), end_date=date(2026, 11, 29),
         venue="Kenya National Theatre", county="Nairobi", source_url="https://kenyabuzz.com/events"),
    dict(slug="solfest-2026", title="SolFest 2026", category="festival",
         description="Sauti Sol's music festival returns to Nairobi.",
         organizer="Sol Generation / Sauti Sol", start_date=date(2026, 12, 17), end_date=date(2026, 12, 19),
         county="Nairobi", source_url="https://www.kbc.co.ke/?p=140993"),
    dict(slug="africa-tech-summit-nairobi-2027", title="Africa Tech Summit Nairobi 2027", category="technology",
         description="A summit for Africa's tech leaders, founders and investors. A Founders Day is held on 9 February.",
         organizer="Africa Tech Summit", start_date=date(2027, 2, 10), end_date=date(2027, 2, 11),
         date_note="Founders Day on 9 February 2027", venue="Sarit Expo Centre, Westlands", county="Nairobi",
         source_url="https://www.africatechsummit.com/nairobi/register/",
         registration_url="https://www.africatechsummit.com/nairobi/register/"),
]

_META_FIELDS = ("news_category", "source_name", "source_url", "source_published_at", "is_featured", "feature_rank",
                "is_trending", "trending_note", "is_breaking", "is_editors_pick")


def seed(admin=None, now=None):
    """Create and publish any launch stories/events that don't exist yet."""
    created_stories = created_events = 0
    for s in STORIES:
        if NewsArticleMeta.query.filter_by(source_url=s["source_url"]).first():
            continue
        article = cms_service.create_news_article(
            {"title": s["title"], "summary": s["summary"], "body": s.get("body") or s["summary"],
             "category": NEWS_CATEGORY_LABELS[s["news_category"]]}, admin)
        meta = NewsArticleMeta(article_id=article.id, is_external=True)
        for f in _META_FIELDS:
            if f in s:
                setattr(meta, f, s[f])
        db.session.add(meta)
        article.status = "published"
        article.published_at = now or datetime.now(timezone.utc)
        db.session.commit()
        created_stories += 1
    for e in EVENTS:
        if NewsEvent.query.filter_by(slug=e["slug"]).first():
            continue
        db.session.add(NewsEvent(publication_status="published", **e))
        db.session.commit()
        created_events += 1
    return {"stories": created_stories, "events": created_events}
