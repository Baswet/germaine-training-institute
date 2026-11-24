const fs = require("fs");
const d = require("docx");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, ShadingType, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,
  Footer, Header, VerticalAlign, TableLayoutType } = d;
const NAVY = "1B2E6B", RED = "C81B3E";
const crest = fs.readFileSync("crest.jpg");
const font = "Times New Roman";
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const dots = () => new TextRun({ children: [new d.Tab()] });
const TABS = [{ type: d.TabStopType.RIGHT, position: 9740, leader: d.LeaderType.DOT }];
const bold = (t) => new TextRun({ text: t, bold: true, font, size: 23 });
const plain = (t) => new TextRun({ text: t, font, size: 23 });
const line = (runs, after = 220, align) => new Paragraph({ children: runs, spacing: { after, line: 276 }, alignment: align, tabStops: TABS });

// header: GERMAINE | crest | INSTITUTE, red rules under the words
const W = 9746; // A4 text width at 0.85in margins ~ (11906 - 2*1080)
const cw = [3900, 1946, 3900];
const word = (t, align) => new TableCell({ width: { size: align === AlignmentType.RIGHT ? cw[0] : cw[2], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
  borders: { top: none, left: none, right: none, bottom: { style: BorderStyle.SINGLE, size: 14, color: RED } },
  children: [new Paragraph({ alignment: align, children: [new TextRun({ text: t, bold: true, font: "Arial", size: 50, color: NAVY })] })] });
const header = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: cw, layout: TableLayoutType.FIXED, borders: noBorders, rows: [new TableRow({ children: [
  word("GERMAINE", AlignmentType.RIGHT),
  new TableCell({ width: { size: cw[1], type: WidthType.DXA }, borders: { top: none, bottom: none, left: none, right: none },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "jpg", data: crest, transformation: { width: 118, height: 110 } })] })] }),
  word("INSTITUTE", AlignmentType.LEFT),
] })] });

// footer boxes
const boxes = [["Pioneer Plaza 3rd Floor Opp.", "Mosque, Mburu Gichua Road,", "Nakuru City"], ["+254 719 488 112", "+254 102 010 874"],
  ["P.O. Box 12290-20100", "Nakuru"], ["germainetraininginstitute", "@gmail.com", "www.germaineinstitute.com"]];
const bw = Math.floor(W / 4);
const whiteB = { style: BorderStyle.SINGLE, size: 12, color: "FFFFFF" };
const footer = new Footer({ children: [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "REGISTERED AND LICENCED Reg No. TVETA/TVC/0029/2020", font: "Arial", size: 14, color: "737885" })] }),
  new Table({ width: { size: bw * 4, type: WidthType.DXA }, columnWidths: [bw, bw, bw, bw], layout: TableLayoutType.FIXED, rows: [new TableRow({ children: boxes.map(lines => new TableCell({
    width: { size: bw, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER, shading: { type: ShadingType.CLEAR, color: "auto", fill: NAVY },
    borders: { top: whiteB, bottom: whiteB, left: whiteB, right: whiteB }, margins: { top: 80, bottom: 80, left: 60, right: 60 },
    children: lines.map(l => new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: l, bold: true, font: "Arial", size: 15, color: "FFFFFF" })] })) })) })] }),
  new Paragraph({ spacing: { before: 40 }, border: { bottom: { style: BorderStyle.DOUBLE, size: 6, color: RED, space: 1 } }, children: [] }),
] });

const body = [
  header,
  new Paragraph({ spacing: { after: 240 }, children: [] }),
  line([bold("To")], 200),
  line([bold("National Government Constituency development Fund (NG-CDF)"), dots()]),
  line([bold("National Government Affirmative Action Fund (NGAAF)"), dots()]),
  line([bold("County Bursary Committee (County & Ward)"), dots()]),
  line([bold("Other Funding Organizations"), dots()]),
  line([bold("Thro!")]),
  line([bold("Chief/Sub-Chief (Location/Sub-location)"), dots()], 0),
  line([plain("(Chief/Sub-Chief to sign and stamp)")], 360),
  new Paragraph({ tabStops: TABS, spacing: { after: 240 }, children: [new TextRun({ text: "REF: Bursary Application for ", bold: true, underline: {}, font, size: 23 }), dots()] }),
  new Paragraph({ tabStops: TABS, spacing: { after: 120, line: 400 }, alignment: AlignmentType.LEFT, children: [plain("This is to bring to your attention that the above named person is a student at Germaine Training Institute. He/she is studying a course leading to the award of Diploma/Certificate/Artisan in "), dots()] }),
  new Paragraph({ spacing: { after: 240, line: 400 }, alignment: AlignmentType.JUSTIFIED, children: [plain("He/she have indicated that is facing financial difficulties in meeting the tuition fee. This letter is to kindly request you to facilitate the holder apply for bursary. For any clarifications or for further details do not hesitate to contact the undersigned.")] }),
  line([plain("Yours faithfully,")], 1000),
  line([plain("Mr. Douglas Onsare")], 0),
  line([plain("Chief Principal")], 0),
];

const doc = new Document({
  creator: "Germaine Training Institute", title: "Bursary Recommendation Letter (template)",
  styles: { default: { document: { run: { font, size: 23 } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 700, bottom: 1300, left: 1080, right: 1080, footer: 400 } } },
    footers: { default: footer }, children: body }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("GTI-Bursary-Recommendation-Letter-Template.docx", b); console.log("ok", b.length); });
