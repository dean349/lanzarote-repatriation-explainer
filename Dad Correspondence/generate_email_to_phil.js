const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  WidthType,
  BorderStyle,
  AlignmentType,
  ShadingType,
  UnderlineType,
  convertInchesToTwip,
} = require("docx");
const fs = require("fs");
const path = require("path");

// ─── Helpers ──────────────────────────────────────────────────────────────────

const bold = (text) => new TextRun({ text, bold: true });
const normal = (text) => new TextRun({ text });
const link = (text) =>
  new TextRun({ text, color: "1155BB", underline: { type: UnderlineType.SINGLE } });

const p = (...runs) =>
  new Paragraph({ children: Array.isArray(runs[0]) ? runs[0] : runs, spacing: { after: 100 } });

const blank = () => new Paragraph({ children: [], spacing: { after: 80 } });

const rule = () =>
  new Paragraph({
    children: [],
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC" } },
    spacing: { after: 160 },
  });

const h2 = (text) =>
  new Paragraph({
    children: [new TextRun({ text, bold: true, size: 26, color: "1A1A2E" })],
    spacing: { before: 280, after: 80 },
  });

const bullet = (text) =>
  new Paragraph({
    children: [normal(text)],
    bullet: { level: 0 },
    spacing: { after: 60 },
  });

const numberedBullet = (text, num) =>
  new Paragraph({
    children: [normal(`${num}.  ${text}`)],
    indent: { left: convertInchesToTwip(0.3) },
    spacing: { after: 60 },
  });

const callout = (text, colour = "7777BB") =>
  new Paragraph({
    children: [new TextRun({ text: "ℹ  " + text, color: "444466", italics: true })],
    indent: { left: convertInchesToTwip(0.4) },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: colour } },
    spacing: { before: 80, after: 120 },
  });

const warningCallout = (text) =>
  new Paragraph({
    children: [new TextRun({ text: "⚠  " + text, color: "7A4400", italics: false })],
    indent: { left: convertInchesToTwip(0.4) },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: "E8A000" } },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "FFFBF0" },
    spacing: { before: 80, after: 120 },
  });

const subh = (text) =>
  new Paragraph({
    children: [new TextRun({ text, bold: true, size: 22, color: "333355" })],
    spacing: { before: 200, after: 60 },
  });

// ─── Gmail search table ───────────────────────────────────────────────────────

const searchTerms = [
  ["Wincham", "Any emails from Wincham Accountants — could be anything about the company"],
  ["Los Romeros", "Any emails mentioning the company name"],
  ["Lanzarote", "Any emails about the villa or property"],
  ["Purvis", "Emails from or about the previous owners of the company"],
  ["Stockwell", "Emails from or about another previous owner"],
  ["share purchase", "Emails about buying the company shares"],
  ["adrem", "Emails from Adrem Accounting (they took over from Wincham later)"],
];

const headerShade = { type: ShadingType.CLEAR, color: "auto", fill: "1A1A2E" };
const rowShade = (i) => ({ type: ShadingType.CLEAR, color: "auto", fill: i % 2 === 0 ? "F3F3FA" : "FFFFFF" });

const makeRow = (cells, shading, isHeader = false) =>
  new TableRow({
    children: cells.map(
      (text, i) =>
        new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text,
                  bold: isHeader || i === 0,
                  color: isHeader ? "FFFFFF" : "111111",
                  size: isHeader ? 20 : 19,
                }),
              ],
              spacing: { before: 80, after: 80 },
            }),
          ],
          shading,
          margins: { top: 40, bottom: 40, left: 80, right: 80 },
          width: i === 0 ? { size: 2200, type: WidthType.DXA } : { size: 6200, type: WidthType.DXA },
        })
    ),
  });

const searchTable = new Table({
  columnWidths: [2200, 6200],
  width: { size: 8400, type: WidthType.DXA },
  rows: [
    makeRow(["Search Term", "What You're Looking For"], headerShade, true),
    ...searchTerms.map(([term, desc], i) => makeRow([term, desc], rowShade(i))),
  ],
});

// ─── Document ─────────────────────────────────────────────────────────────────

const doc = new Document({
  styles: {
    paragraphStyles: [
      { id: "Normal", name: "Normal", run: { font: "Calibri", size: 22 } },
    ],
  },
  sections: [
    {
      properties: {
        page: { margin: { top: 900, bottom: 900, left: 1000, right: 1000 } },
      },
      children: [
        // ── Header ──
        p(bold("TO: "), normal("Phil Harrison")),
        p(bold("FROM: "), normal("Dean Harrison")),
        p(bold("SUBJECT: "), normal("Los Romeros Limited — Important: A Few Questions I Need Your Help With")),
        p(bold("DATE: "), normal("1 April 2026")),
        rule(),

        p(normal("Hi Dad,")),
        blank(),
        p(normal("I hope you're well. As you know, I've been working with some specialist advisers to get everything in order for the company and the Lanzarote property, and we're making good progress.")),
        blank(),
        p(normal("To make sure all the legal and tax records are completely accurate — especially for the winding-up process (the MVL) — I need your help confirming a few specific facts that only you will have the paperwork for.")),
        blank(),
        p(bold("Please can you find and send me the following:")),
        rule(),

        // ── Section 1 ──
        h2("1. The Agreement / Contract You Signed with Wincham"),
        p(normal("When you and Mum agreed to take over Los Romeros Limited, Wincham should have given you a document to sign — this might be called:")),
        bullet('A "Share Purchase Agreement" or "Sale Agreement"'),
        bullet("A letter from Wincham confirming the deal"),
        bullet("A contract or terms document"),
        blank(),
        p(bold("What I need to know from it:")),
        bullet("The exact date you signed it (or the date shown on the document)"),
        bullet("The total amount you paid for the company (i.e. what you paid Wincham or the previous owners for the shares / for the right to own the company and the property)"),
        blank(),
        callout("Why this matters: The tax office (HMRC) uses the date of the agreement as the starting point for calculating any tax when the property is eventually sold. Getting this date right could make a significant difference to your tax bill."),
        rule(),

        // ── Section 2 ──
        h2("2. How You Paid"),
        bullet("Did you pay the purchase price in a lump sum? Or in instalments?"),
        bullet("Do you have any bank statements or payment receipts showing when money was transferred to Wincham?"),
        bullet("Was there a deposit paid first, and then a final balance? If so, when were each of these paid?"),
        blank(),
        warningCallout("Before you send me any bank statements: I only need to see the transactions — NOT your account number, sort code, or any other personal details. Please black these out first. The instructions below show you exactly how to do this — it takes about 2 minutes."),
        rule(),

        // ── Redaction box ──
        h2("🔒 How to Black Out Your Bank Details Before Sending"),
        p(normal("I completely understand you may not want to send me your full account number or sort code — and you don't need to. I only need to see the dates and amounts of any payments to Wincham. Here is the simplest way to do it:")),
        blank(),

        subh("✅ The Easiest Way — Use Your Phone (Recommended)"),
        p(normal("This takes about 2 minutes and uses nothing but your phone:")),
        blank(),
        numberedBullet("Print your bank statement on paper (or if it's a PDF, just take a photo of the screen)", 1),
        numberedBullet("Take a clear photo of it with your phone", 2),
        numberedBullet("Open the photo on your phone and tap Edit (pencil icon)", 3),
        numberedBullet("Look for a Draw or Pen tool — usually a small pencil or marker icon", 4),
        numberedBullet("Choose a thick black pen and draw a solid line over your account number (8 digits) and sort code (12-34-56)", 5),
        numberedBullet("Save the edited photo and send it to me on WhatsApp as normal", 6),
        blank(),
        callout("If you're not sure how to use the pen/draw tool on your phone, just give me a call and I will walk you through it — it takes about one minute."),
        blank(),

        subh("💻 Alternative — If the Statement is a PDF on Your Chromebook"),
        p(normal("If your bank sends PDF statements by email and you'd rather do it on your Chromebook, use this free website — no downloading needed:")),
        blank(),
        numberedBullet("Open your Chromebook and go to: https://www.ilovepdf.com/redact-pdf", 1),
        numberedBullet('Click "Select PDF file" and choose your bank statement', 2),
        numberedBullet("Once it loads, draw a black box over your account number and sort code using your mouse", 3),
        numberedBullet('Click "Redact PDF" and then download the blacked-out version', 4),
        numberedBullet("Email it to me or send it via WhatsApp", 5),
        blank(),
        callout("Most people find the phone method easier — only try the website if you prefer working on your Chromebook."),
        rule(),

        // ── Section 3 ──
        h2("3. Who You Were Buying From"),
        p(normal("The Companies House records show that before you and Mum took over, the previous owners were the "), bold("Purvis family"), normal(" (Frederick and Margaret Purvis). However, I need to confirm:")),
        bullet("Did Wincham act as the middleman organising the sale on behalf of the Purvises?"),
        bullet("Or did you deal with Wincham directly as if they were the seller?"),
        bullet("Do you have any correspondence (letters or emails) from Wincham from 2019 arranging the purchase?"),
        rule(),

        // ── Section 4 ──
        h2("4. Did You Use a Solicitor?"),
        bullet("Did Wincham arrange everything themselves, or did you use your own solicitor?"),
        bullet("If you used a solicitor, do you have their name and the paperwork they produced?"),
        blank(),
        callout("This is important for the negligence case against Wincham. If Wincham handled the whole transaction themselves without advising you to get independent legal advice, that is a significant part of what they did wrong."),
        rule(),

        // ── Section 5 ──
        h2("5. Quick Confirmation of Basic Facts"),
        bullet("Your full date of birth (month and year is fine)"),
        bullet("Mum's full date of birth (month and year is fine)"),
        bullet("Your home address as it was in 2019 (when you took over the company)"),
        bullet("Whether you were both retired at the time you took on the company"),
        rule(),

        // ── What to do next ──
        h2("What to Do Next — Paperwork AND Your Emails"),
        p(normal("The most important thing is to look through any paperwork Wincham sent you in 2018–2019 — it might be a folder, a welcome pack, or a bundle of letters. Even a single letter with a date on it would be enormously helpful.")),
        blank(),
        p(normal("But just as important are your emails. Even if you don't remember saving anything, there is a very good chance that emails from Wincham are still sitting in your Gmail inbox, deleted folder, or spam — Gmail keeps almost everything going back years unless you manually deleted it.")),
        rule(),

        // ── Step 1 ──
        h2("📱 Step 1 — Watch This Short Video on Your Phone First"),
        p(normal("Before you start searching your emails on your Chromebook, watch this short YouTube video on your phone. It is under 2 minutes long and shows you exactly how to search for old emails in Gmail, step by step, for beginners:")),
        blank(),
        new Paragraph({ children: [bold('▶️  "How to Find Old Emails in Gmail"')], indent: { left: convertInchesToTwip(0.4) }, spacing: { after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: "🔗  " }), link("https://www.youtube.com/watch?v=SvfsUW9ml0k")], indent: { left: convertInchesToTwip(0.4) }, spacing: { after: 60 } }),
        new Paragraph({ children: [normal("⏱️  Duration: 1 minute 56 seconds  |  👁️ Over 564,000 views")], indent: { left: convertInchesToTwip(0.4) }, spacing: { after: 120 } }),
        p(normal("Just open that link on your phone, watch it all the way through, and then follow the steps below on your Chromebook.")),
        rule(),

        // ── Step 2 ──
        h2("💻 Step 2 — Search Your Gmail on Your Chromebook"),
        p(normal("Once you've watched the video, open Gmail on your Chromebook and use the search bar at the top to search for the following, one at a time:")),
        blank(),
        searchTable,
        blank(),
        p(normal("For each search term, look in:")),
        bullet("Your main inbox (all results)"),
        bullet("Your Sent folder (anything you sent back to them)"),
        bullet("Your Trash / Deleted folder"),
        bullet("Your Spam folder"),
        blank(),
        callout('Tip: In Gmail, you can search inside a specific folder by typing something like: from:wincham or subject:Lanzarote in the search bar. The video will show you exactly how to do this.'),
        rule(),

        // ── Step 3 ──
        h2("📸 Step 3 — Take a Photo or Screenshot of Anything You Find"),
        bullet("Forward emails to me directly from Gmail, or"),
        bullet("Take a photo on your phone of the screen and send it to me on WhatsApp"),
        blank(),
        p(normal("Please don't worry if some of this is hard to find — just send whatever you have and I'll work with it. The more we have, the stronger our position.")),
        rule(),

        blank(),
        p(normal("Thanks Dad, speak soon.")),
        blank(),
        p(bold("Dean")),
      ],
    },
  ],
});

const outputPath = path.join(__dirname, "Email_to_Phil_Harrison_01Apr2026.docx");
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  console.log("✅  Word document created: " + outputPath);
}).catch((err) => {
  console.error("❌  Error:", err.message);
});
