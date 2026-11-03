#!/usr/bin/env python3
"""Universal Deep Stylometric, Forced-Trend & Anti-Scam Scanner (v5.2).

Evaluates 18 linguistic, structural, rhythmic, cognitive, and marketing-hype indicators:
  1. Em-dash density (ignoring fenced code blocks and inline code)
  2. Multilingual stock AI vocabulary (EN, VI, ES, FR, DE, ZH, JA, KO) with context-aware matching
  3. Negative parallelisms ('Not just X, it's Y' across languages)
  4. Superficial participial/gerund commentary tails (', highlighting/ensuring/qua đó...')
  5. Copula inflation/avoidance ('serves as / stands as / boasts')
  6. See-saw concession clauses ('While/Although X is important, Y...' including line starts)
  7. Rhetorical self-Q&A micro-clichés ('The result?', 'The catch?', 'Why does this matter?')
  8. Pedagogical lecture & colon-split title frames ('To understand X, we must...', 'Title: How X Y')
  9. Abstract nominalization density without concrete numeric anchors
 10. Framing tells (false universal ranges, weasel attributions, self-referential narration)
 11. Mechanical transition stacking ('Furthermore,', 'Moreover,', 'Hơn thế nữa,')
 12. Forced trend-jacking / news-peg clichés ('With the recent rise of...', 'Trước làn sóng...')
 13. Scam / hype marketing triggers ('10x your', 'secret blueprint', 'limited spots', exclamation inflation)
 14. Symmetrical rule-of-three triads ('A, B, and C', ignoring number lists & day/month names)
 15. Formatting & bold-lead bullet soup ('- **Label**: ...')
 16. Decorative emoji clutter
 17. Sentence-length burstiness (Coefficient of Variation CV & SD, CJK & newline-fallback aware)
 18. Paragraph geometry uniformity & consecutive sentence-opener repetition

Zero external dependencies (Python 3.10+).
Usage:
  python3 tools/slop_scan.py FILE [--fix-hints] [--json] [--strip-markdown] [--max-score N]
  cat FILE | python3 tools/slop_scan.py - [--fix-hints]
  python3 tools/slop_scan.py --selftest
  python3 tools/slop_scan.py --version
"""
import argparse
import json
import re
import sys

__version__ = "5.2.0"

# --- Multilingual Lexical Blacklists ---
STOCK_EN = [
    "delve", "delves", "delving", "tapestry", "the realm of", "pivotal", "seamless", "seamlessly",
    "robust", "game-changer", "game changer", "leveraging", "leverages", "leveraged",
    "elevate", "elevates", "elevating", "unlock", "unlocks", "unlocking",
    "unleash", "unleashes", "unleashing", "landscape", "crucial",
    "vital role", "vital for", "is vital", "vital to",
    "meticulous", "meticulously", "multifaceted", "holistic", "synergy", "paradigm",
    "beacon", "cornerstone", "catalyst", "catalyze", "spearhead", "spearheading",
    "foster", "fosters", "fostering", "underscore", "underscores", "underscoring",
    "empower", "empowers", "empowering",
    "streamline", "streamlines", "streamlining", "revolutionize", "revolutionizes",
    "revolutionizing", "transformative", "indelible", "embark", "embarking",
    "ever-evolving", "in today's fast-paced", "in today's digital age", "it's important to note",
    "it is important to note", "it's worth noting", "plays a pivotal role",
    "plays a crucial role", "stands as a testament", "serves as a testament", "indelible mark",
    "in conclusion", "i hope this helps", "i'd be happy to", "certainly!", "let's dive in",
    "without further ado", "a testament to", "sits at the intersection", "strikes a balance",
    "at the heart of", "paves the way", "plethora", "myriad", "cutting-edge", "groundbreaking",
    "north star", "double-edged sword", "tip of the iceberg", "production-ready",
    "blazingly fast", "comprehensive error handling", "a deep dive into", "in the wake of"
]

STOCK_VI = [
    "trong bối cảnh", "trong kỷ nguyên số", "không thể phủ nhận", "như chúng ta đã biết",
    "hãy cùng khám phá", "tóm lại,", "đóng vai trò quan trọng", "đóng vai trò then chốt",
    "mang đến trải nghiệm", "một cách toàn diện", "chìa khóa vàng", "kim chỉ nam",
    "mở ra cánh cửa", "khẳng định vị thế", "tạo tiền đề", "góp phần nâng cao",
    "mang lại cái nhìn sâu sắc", "hành trình khám phá", "không ngừng phát triển",
    "tối ưu hóa trải nghiệm", "bức tranh toàn cảnh"
]

STOCK_MULTILINGUAL = [
    "en el vertiginoso mundo", "juega un papel fundamental", "es importante destacar",
    "un tapiz de", "en conclusión", "en conclusion",
    "dans un monde en constante évolution", "joue un rôle crucial", "il est important de noter",
    "une pléthore de",
    "in der heutigen schnelllebigen welt", "spielt eine entscheidende rolle",
    "es ist wichtig zu beachten"
]

# Rule 58 CJK phrases (matched via substring since CJK does not use whitespace word boundaries)
STOCK_CJK = [
    "在当今快节奏的", "不仅仅", "发挥着至关重要的作用", "总而言之", "让我们一起探索",
    "において重要な役割を果たしています", "重要な役割を果たしています", "単なる",
    "と言っても過言ではありません", "結論として",
    "오늘날 빠르게 변화하는", "단순히", "일 뿐만 아니라", "중요한 역할을 합니다"
]

# Context-aware verb-like use of "leverage" (excludes noun compounds like "leverage ratio", "debt leverage")
LEVERAGE_NOUN_PREFIX = re.compile(
    r"(?:financial|debt|operating|mechanical|high|low|maximum|excessive|credit|capital|net|total|more|less|of|word|verb|noun)\s+[`'\"]*$",
    re.I,
)
LEVERAGE_NOUN_SUFFIX = re.compile(
    r"^\s+(?:ratio|ratios|buyout|buyouts|limit|limits|point|points|multiple|effect|level|levels)\b",
    re.I,
)
LEVERAGE_WORD = re.compile(r"(?<!\w)leverage(?!\w)", re.I)

# Context-aware verb-like marketing use of "harness"/"harnessing" (e.g. "harness the/your/our/power of")
HARNESS_VERB_RE = re.compile(
    r"\bharness(?:es|ed|ing)?\s+(?:the|your|our|their|its|this|full|new|true|ai|data|cloud|modern|power\s+of|potential\s+of)\b",
    re.I,
)

# Day and month names/abbreviations to ignore in Rule-of-Three triad detection
CALENDAR_TOKENS = {
    "mon", "tue", "tues", "wed", "thu", "thur", "thurs", "fri", "sat", "sun",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "january", "february", "march", "april", "june", "july", "august", "september",
    "october", "november", "december"
}

# --- Cross-Linguistic Syntactic & Cognitive Regexes ---
# 1. Negative Parallelisms ("Not just X, but Y" + CJK equivalents)
NOT_JUST = re.compile(
    r"(?:\b(?:it['’]?s|this is|that['’]?s|isn['’]?t|aren['’]?t|not|more than)\s+"
    r"(?:just|only|merely|simply)\b[^.\n]{1,90}?[,;—–-]?\s*(?:but|it['’]?s|it is|they['’]?re|rather)\b)"
    r"|(?:không\s+(?:chỉ|đơn thuần|những)[^.\n]{1,100}?mà\s+(?:còn|là))"
    r"|(?:\bno\s+es\s+solo\b[^.\n]{1,80}?\bsino\b)"
    r"|(?:\bce\s+n['’]est\s+pas\s+seulement\b[^.\n]{1,80}?\bmais\b)"
    r"|(?:\bnicht\s+nur\b[^.\n]{1,80}?\bsondern\s+auch\b)"
    r"|(?:不仅[^。！？\n]{1,40}?而且)"
    r"|(?:単なる[^。！？\n]{1,40}?ではなく)"
    r"|(?:단순히[^.!?\n]{1,40}?뿐만\s*아니라)",
    re.I,
)

# 2. Superficial Participial / Gerund Commentary Tails
PARTICIPIAL_TAIL = re.compile(
    r"(?:,\s+(?:highlighting|underscoring|showcasing|reflecting|ensuring|fostering|"
    r"demonstrating|illustrating|emphasizing|paving the way for|contributing to|"
    r"reinforcing|solidifying|symbolizing|empowering|enabling)\b[^.\n]{3,90}[.!?])"
    r"|(?:,\s+(?:qua đó|từ đó|góp phần)\s+(?:khẳng định|nâng cao|tạo nên|thúc đẩy|mở ra|đảm bảo)[^.\n]{3,90}[.!?])",
    re.I,
)

# 3. Copula Avoidance / Inflation
COPULA_AVOID = re.compile(
    r"\b(?:serves as|stands as|functions as|acts as|boasts a|boasts an|"
    r"được xem như là một minh chứng|đóng vai trò như một)\b",
    re.I,
)

# 4. See-Saw Concession Clauses ("While X is important, Y..." at start of string, after punctuation, or at start of any line)
SEESAW_CONCESSION = re.compile(
    r"(?:^|(?<=[.!?]\s)|(?<=\n))\s*(?:While|Although|Even though|Despite the fact that|Mặc dù|Dù cho)\s+"
    r"[^,\n]{6,85},\s+[^.\n]{8,120}[.!?]",
    re.I | re.M,
)

# 5. Rhetorical Self-Q&A Micro-Clichés ("The result?", "The catch?", "Why does this matter?")
SELF_QA = re.compile(
    r"(?:^|(?<=[.!?\n])\s*)(?:The result\?|The catch\?|The best part\?|The bottom line\?|"
    r"The kicker\?|Here['’]?s the kicker:|Why does this matter\?|What does this mean\?|"
    r"Sound familiar\?|Kết quả là gì\?|Điểm đặc biệt là gì\?|Tại sao điều này quan trọng\?)",
    re.I | re.M,
)

# 6. Pedagogical Lecture Framing & Colon-Brochure Headings
LECTURE_FRAME = re.compile(
    r"\b(?:to truly understand|before diving into|let['’]?s take a step back|at its core,|in essence,|"
    r"để hiểu rõ hơn về|trước khi đi sâu vào)\b",
    re.I,
)
COLON_HEADING = re.compile(
    r"^#{1,3}\s+[\w\s'-]{4,35}:\s+(?:How|Why|The|A|Unlocking|Mastering|Navigating|Khám phá|Tối ưu|Bí quyết)\b",
    re.I | re.M,
)

# 7. False Universal Ranges, Weasel Attributions & Self-Reference
FALSE_RANGE = re.compile(
    r"(?:\bfrom\s+[\w\s]{2,25}\s+to\s+(?:fortune 500|enterprises|seasoned|industry leaders|global|everyday|execution)\b)"
    r"|(?:từ\s+người\s+mới\s+bắt\s+đầu\s+đến\s+chuyên\s+gia)",
    re.I,
)
WEASEL_ATTR = re.compile(
    r"\b(?:experts argue|experts say|industry observers note|studies have shown|many believe|"
    r"nhiều chuyên gia cho rằng|các nghiên cứu chỉ ra rằng)\b",
    re.I,
)
SELF_REF = re.compile(
    r"\b(?:this article explores|this document outlines|this section provides an overview|"
    r"bài viết này sẽ khám phá|trong bài viết này chúng ta sẽ)\b",
    re.I,
)

# 8. Mechanical Transition Stacking
TRANSITION_STACK = re.compile(
    r"(?:^|(?<=[.!?]\s)|(?<=\n))\s*(?:Furthermore|Moreover|Additionally|Consequently|In addition|Ultimately|"
    r"Hơn thế nữa|Bên cạnh đó|Ngoài ra|Thêm vào đó|Tóm lại)\s*,",
    re.I,
)

# 9. Abstract Nominalization Suffixes (EN + VI)
ABSTRACT_NOUNS_EN = re.compile(
    r"\b\w{5,}(?:tion|ment|ity|ness|ance|ence|ism)\b",
    re.I,
)
ABSTRACT_NOUNS_VI = re.compile(
    r"\b(?:sự|việc)\s+(?:tối ưu hóa|phát triển|triển khai|thực hiện|chuyển đổi|tăng trưởng|cải thiện|tích hợp)\b",
    re.I,
)
CONCRETE_NUMBER = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")

# 10. Forced Trend-Jacking / Cringe News-Pegging (v5.1)
FORCED_TREND = re.compile(
    r"\b(?:with the recent (?:rise|explosion|surge|boom) of|in light of recent (?:events|trends)|"
    r"as we all saw this week|as [\w\s]{2,20} continues to take the world by storm|"
    r"trước làn sóng|với sự bùng nổ của|như chúng ta đã thấy trong thời gian gần đây)\b",
    re.I,
)

# 11. Scam / "Lùa Gà" Marketing Hype Triggers (v5.1)
SCAM_HYPE = re.compile(
    r"\b(?:10x your|skyrocket your|explode your|guaranteed roi|secret blueprint|underground method|"
    r"what the gurus won['’]?t tell you|spots are filling up fast|act now before it['’]?s too late|"
    r"once-in-a-lifetime opportunity|financial freedom|passive income machine|prefer staying broke|"
    r"cam kết lợi nhuận|bí mật triệu đô|công thức bí truyền|chỉ còn duy nhất \d+ suất|"
    r"đăng ký ngay kẻo lỡ|tự do tài chính|lùa gà)\b",
    re.I,
)

# 12. Rule-of-three triads ("X, Y, and Z") - requires alphabetic start on each item to ignore pure numbers
TRIAD_RAW = re.compile(
    r"\b([A-Za-z\u00C0-\u024F\u1E00-\u1EFF][\w-]*),\s+"
    r"([A-Za-z\u00C0-\u024F\u1E00-\u1EFF][\w-]*),\s+"
    r"(?:and|or|và)\s+"
    r"([A-Za-z\u00C0-\u024F\u1E00-\u1EFF][\w-]*)\b",
    re.I,
)

# 13. Bold-lead bullet items ("- **Header**: text")
BOLD_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+\*\*[^*]+\*\*\s*[:—–-]", re.M)

# 14. Decorative Emojis
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2705\u2728\u2B50\U0001F680\U0001F525\U0001F4A1]")

# CJK character range + non-CJK word token regex
CJK_CHAR_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]")
NON_CJK_WORD_RE = re.compile(r"[A-Za-z0-9_\u00C0-\u024F\u1E00-\u1EFF]+")

# Code block stripping regexes
FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def normalize_quotes(text: str) -> str:
    """Normalize curly apostrophes and quotes to straight ASCII equivalents."""
    return (
        text.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


def strip_code_segments(text: str) -> str:
    """Remove fenced code blocks and inline code spans."""
    no_fenced = FENCED_CODE_RE.sub(" ", text)
    return INLINE_CODE_RE.sub(" ", no_fenced)


def strip_markdown_syntax(text: str) -> str:
    """Strip YAML frontmatter, code blocks, inline code, blockquotes, and quoted negative examples."""
    t = re.sub(r"\A---\n[\s\S]*?\n---\n?", "", text)
    t = strip_code_segments(t)
    t = re.sub(r"^\s*>.*$", "", t, flags=re.M)
    t = normalize_quotes(t)
    t = re.sub(r'\*"[^"\n]{1,140}"\*', " ", t)
    t = re.sub(r'"[^"\n]{1,140}"', " ", t)
    t = re.sub(r"^\s*\|[\s|:-]+\|\s*$", "", t, flags=re.M)
    return t


def tokenize_words(text: str) -> list[str]:
    """Return word tokens for alphabetic scripts plus individual CJK characters."""
    non_cjk_text = CJK_CHAR_RE.sub(" ", text)
    words = NON_CJK_WORD_RE.findall(non_cjk_text)
    cjk_chars = CJK_CHAR_RE.findall(text)
    return words + cjk_chars


def split_sentences(text: str) -> list[str]:
    """Split text into sentences across Latin and CJK punctuation, with newline fallback."""
    stripped = text.strip()
    if not stripped:
        return []
    has_terminal = bool(re.search(r"[.!?।。！？]", stripped))
    if has_terminal:
        parts = [s.strip() for s in re.split(r"(?<=[.!?।。！？])\s*", stripped) if s.strip()]
        lines = [l.strip() for l in stripped.splitlines() if l.strip()]
        if len(parts) <= 1 and len(lines) > 1:
            return lines
        return parts
    return [l.strip() for l in stripped.splitlines() if l.strip()]


def count_verb_leverage(text: str) -> int:
    """Count 'leverage' only when used as a verb (excluding 'leverage ratio', 'debt leverage', etc.)."""
    count = 0
    for m in LEVERAGE_WORD.finditer(text):
        prefix = text[max(0, m.start() - 25):m.start()]
        suffix = text[m.end():min(len(text), m.end() + 25)]
        if LEVERAGE_NOUN_PREFIX.search(prefix) or LEVERAGE_NOUN_SUFFIX.search(suffix):
            continue
        count += 1
    return count


def count_marketing_harness(text: str) -> int:
    """Count 'harness'/'harnessing' only when used as a verb in marketing phrasing."""
    return len(HARNESS_VERB_RE.findall(text))


def find_valid_triads(text: str) -> list[tuple[str, str, str]]:
    """Find 'X, Y, and Z' triads while ignoring pure numbers and day/month abbreviations."""
    results = []
    for m in TRIAD_RAW.finditer(text):
        w1, w2, w3 = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
        if {w1, w2, w3}.issubset(CALENDAR_TOKENS):
            continue
        results.append((w1, w2, w3))
    return results


def scan(text: str, strip_md: bool = False) -> dict:
    working_text = strip_markdown_syntax(text) if strip_md else text
    norm_text = normalize_quotes(working_text)

    tokens = tokenize_words(norm_text)
    words = max(len(tokens), 1)
    per1k = lambda n: (n * 1000.0) / words

    hits = []
    fix_hints = []
    score = 0

    # 1. Em-dashes (always ignore fenced code blocks and inline code)
    code_free_text = strip_code_segments(working_text)
    dash = code_free_text.count("—") + code_free_text.count(" -- ")
    if per1k(dash) > 2.0:
        pts = min(20, int(per1k(dash) * 3.5))
        score += pts
        hits.append(f"em-dash overuse: {dash} ({per1k(dash):.1f}/1k words) [+{pts}]")
        fix_hints.append("Replace em-dashes (—) with periods, commas, or parentheses. Keep <2 per 1,000 words.")

    # 2. Multilingual Stock Vocabulary (EN + VI + ES/FR/DE + CJK + context-aware 'leverage' & 'harness')
    stock_matches = []
    for phrase in STOCK_EN + STOCK_VI + STOCK_MULTILINGUAL:
        pattern = re.compile(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", re.I)
        count = len(pattern.findall(norm_text))
        if count:
            stock_matches.append((phrase, count))

    lev_verb_count = count_verb_leverage(norm_text)
    if lev_verb_count:
        stock_matches.append(("leverage", lev_verb_count))

    harness_verb_count = count_marketing_harness(norm_text)
    if harness_verb_count:
        stock_matches.append(("harness", harness_verb_count))

    for cjk_phrase in STOCK_CJK:
        c_count = norm_text.count(cjk_phrase)
        if c_count:
            stock_matches.append((cjk_phrase, c_count))

    n_stock = sum(c for _, c in stock_matches)
    if n_stock:
        pts = min(30, n_stock * 7)
        score += pts
        summary = ", ".join(f"'{w}' x{c}" for w, c in stock_matches[:8])
        hits.append(f"stock AI words/phrases ({n_stock} total): {summary} [+{pts}]")
        fix_hints.append("Delete throat-clearing openers and replace abstract AI buzzwords with concrete nouns, numbers, or physical verbs.")

    # 3. Negative Parallelisms
    nj = len(NOT_JUST.findall(norm_text))
    if nj:
        pts = min(20, nj * 10)
        score += pts
        hits.append(f"negative parallelism ('not just X, but Y'): {nj} [+{pts}]")
        fix_hints.append("Cut 'It is not just X, it is Y'. State directly what the subject does.")

    # 4. Superficial Participial / Gerund Tails
    pt = len(PARTICIPIAL_TAIL.findall(norm_text))
    if pt:
        pts = min(18, pt * 9)
        score += pts
        hits.append(f"superficial participial tails (', highlighting/ensuring/qua đó...'): {pt} [+{pts}]")
        fix_hints.append("Delete trailing ', highlighting/ensuring/reflecting...' clauses or split into a separate sentence with a concrete subject.")

    # 5. Copula Avoidance
    cop = len(COPULA_AVOID.findall(norm_text))
    if cop:
        pts = min(12, cop * 6)
        score += pts
        hits.append(f"copula avoidance ('serves as / stands as / boasts'): {cop} [+{pts}]")
        fix_hints.append("Replace 'serves as', 'stands as', or 'boasts' with plain 'is' or 'has'.")

    # 6. See-Saw Concession Clauses ("While X, Y")
    seesaw = len(SEESAW_CONCESSION.findall(norm_text))
    if seesaw >= 2 or (seesaw >= 1 and per1k(seesaw) > 6.0):
        pts = min(16, seesaw * 7)
        score += pts
        hits.append(f"see-saw concession clauses ('While/Although X, Y'): {seesaw} [+{pts}]")
        fix_hints.append("Stop balancing sentences with 'While X is important, Y...'. State the exact boundary threshold directly.")

    # 7. Rhetorical Self-Q&A Micro-Clichés
    sqa = len(SELF_QA.findall(norm_text))
    if sqa:
        pts = min(14, sqa * 7)
        score += pts
        hits.append(f"rhetorical self-Q&A cliché ('The result? / The catch? / Why does this matter?'): {sqa} [+{pts}]")
        fix_hints.append("Remove fake 2-word rhetorical questions ('The result?', 'The catch?') and connect the cause and effect directly.")

    # 8. Pedagogical Lecture Frames & Colon-Brochure Headings
    lf = len(LECTURE_FRAME.findall(norm_text)) + len(COLON_HEADING.findall(norm_text))
    if lf:
        pts = min(10, lf * 5)
        score += pts
        hits.append(f"pedagogical lecture frame or colon-brochure heading: {lf} [+{pts}]")
        fix_hints.append("Cut 'To truly understand X / At its core' and rewrite colon-split headings as a single sharp assertion.")

    # 9. Abstract-to-Concrete Ratio (Nominalization Density without Numbers)
    abs_count = len(ABSTRACT_NOUNS_EN.findall(norm_text)) + (len(ABSTRACT_NOUNS_VI.findall(norm_text)) * 2)
    num_count = len(CONCRETE_NUMBER.findall(norm_text))
    if words >= 40 and per1k(abs_count) > 65 and num_count == 0:
        score += 12
        hits.append(
            f"high abstract nominalization density ({per1k(abs_count):.0f}/1k words) with zero numeric anchors [+12]"
        )
        fix_hints.append("Obey the 35-Word Concrete Floor: replace abstract '-tion/-ment/việc/sự' nouns with actors, active verbs, and exact numbers.")

    # 10. False Ranges, Weasel Attributions & Self-Reference
    fr = len(FALSE_RANGE.findall(norm_text))
    wa = len(WEASEL_ATTR.findall(norm_text))
    sr = len(SELF_REF.findall(norm_text))
    if fr + wa + sr > 0:
        pts = min(15, (fr + wa + sr) * 5)
        score += pts
        hits.append(f"framing tells (false ranges={fr}, weasel attributions={wa}, self-reference={sr}) [+{pts}]")
        fix_hints.append("Name the specific audience, cite exact sources instead of 'experts say', and drop 'This article explores...'.")

    # 11. Mechanical Transition Stacking
    ts = len(TRANSITION_STACK.findall(norm_text))
    if ts >= 2 or (ts >= 1 and per1k(ts) > 10.0):
        pts = min(10, ts * 4)
        score += pts
        hits.append(f"mechanical transition stacking ('Furthermore/Moreover/Hơn thế nữa'): {ts} [+{pts}]")
        fix_hints.append("Remove mechanical transition adverbs at the start of paragraphs; let concrete cause-and-effect link ideas.")

    # 12. Forced Trend-Jacking & Scam/Hype Marketing Triggers (v5.1)
    ft = len(FORCED_TREND.findall(norm_text))
    if ft:
        pts = min(16, ft * 8)
        score += pts
        hits.append(f"forced trend-jacking opener ('With the recent rise/explosion of...'): {ft} [+{pts}]")
        fix_hints.append("Pass market trends through the Organic Fit Gate: drop 'With the recent rise of...' and state the direct operational symptom instead.")

    sh = len(SCAM_HYPE.findall(norm_text))
    exclam = norm_text.count("!")
    if sh or exclam >= 3:
        pts = min(25, sh * 10 + (6 if exclam >= 3 else 0))
        score += pts
        hits.append(f"scam/hype marketing triggers (hype phrases={sh}, exclamation marks={exclam}) [+{pts}]")
        fix_hints.append("Remove scammy ROI multipliers, fake scarcity, and exclamation marks; replace with benevolent boundaries and verifiable math.")

    # 13. Rule-of-Three Triads
    triads = find_valid_triads(norm_text)
    tri = len(triads)
    if per1k(tri) > 4.0 and tri >= 2:
        pts = min(10, int(per1k(tri) * 2))
        score += pts
        hits.append(f"rule-of-three lists ('X, Y, and Z'): {tri} ({per1k(tri):.1f}/1k words) [+{pts}]")
        fix_hints.append("Break symmetrical triplets into single precise words, 2-item contrasts, or uneven 4-item lists.")

    # 14. Formatting & Bold-Lead Bullet Soup
    lines = [l for l in norm_text.splitlines() if l.strip()]
    bullets = sum(1 for l in lines if re.match(r"\s*([-*•]|\d+[.)])\s", l))
    bold_bullets = len(BOLD_BULLET.findall(norm_text))
    if lines and len(lines) > 5 and (bullets / len(lines)) > 0.55:
        score += 10
        hits.append(f"bullet overload: {bullets}/{len(lines)} lines are bullets [+10]")
        fix_hints.append("Convert bullet-heavy explanations into connected prose paragraphs.")
    if bold_bullets >= 4:
        pts = min(10, bold_bullets * 2)
        score += pts
        hits.append(f"bold-lead bullet soup ('- **Label**: ...'): {bold_bullets} items [+{pts}]")
        fix_hints.append("Avoid starting every bullet with a bolded title and colon; write natural sentences or use a table.")

    # 15. Decorative Emojis
    emo = len(EMOJI.findall(norm_text))
    if emo >= 2:
        pts = min(10, emo * 3)
        score += pts
        hits.append(f"decorative emojis: {emo} [+{pts}]")
        fix_hints.append("Strip decorative emojis from headings and prose.")

    # 16. Sentence Rhythm / Burstiness (Language-Agnostic & CJK-Aware Stylometry)
    raw_sents = split_sentences(norm_text)
    sent_lengths = [len(tokenize_words(s)) for s in raw_sents if len(tokenize_words(s)) > 0]
    mean_len = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0.0
    sd_len = (sum((x - mean_len) ** 2 for x in sent_lengths) / len(sent_lengths)) ** 0.5 if sent_lengths else 0.0
    cv_len = (sd_len / mean_len) if mean_len > 0 else 0.0

    if len(sent_lengths) >= 5 and (sd_len < 4.2 or cv_len < 0.28):
        score += 12
        hits.append(
            f"flat sentence rhythm / low burstiness: mean={mean_len:.1f}w, sd={sd_len:.1f}w, CV={cv_len:.2f} [+12]"
        )
        fix_hints.append("Increase burstiness (target CV >= 0.35): follow a 25-word analytical sentence with a sharp 3-6 word sentence.")

    # 17. Paragraph Symmetry & Repetitive Openers
    paras = [p.strip() for p in re.split(r"\n\s*\n", norm_text) if p.strip() and not p.strip().startswith("#")]
    if len(paras) >= 4:
        para_words = [len(tokenize_words(p)) for p in paras]
        p_mean = sum(para_words) / len(para_words)
        p_sd = (sum((x - p_mean) ** 2 for x in para_words) / len(para_words)) ** 0.5
        p_cv = (p_sd / p_mean) if p_mean > 0 else 0.0
        if p_cv < 0.18 and p_mean > 25:
            score += 8
            hits.append(f"uniform paragraph geometry: {len(paras)} paragraphs with flat length variance (CV={p_cv:.2f}) [+8]")
            fix_hints.append("Vary paragraph lengths: mix a punchy 1-2 sentence paragraph with deeper narrative paragraphs.")

    if len(raw_sents) >= 6:
        first_words = [tokenize_words(s)[0].lower() for s in raw_sents if tokenize_words(s)]
        consecutive_repeats = sum(
            1 for i in range(1, len(first_words)) if first_words[i] == first_words[i - 1]
        )
        if consecutive_repeats >= 2:
            score += 6
            hits.append(f"repetitive consecutive sentence openers: {consecutive_repeats} pairs [+6]")
            fix_hints.append("Vary how consecutive sentences start instead of repeating the same subject or determiner.")

    final_score = min(score, 100)
    verdict = (
        "CLEAN (Human-like)" if final_score <= 15
        else "MODERATE (Needs editing)" if final_score <= 35
        else "HIGH SLOP / HYPE (Rewrite required)"
    )
    return {
        "score": final_score,
        "verdict": verdict,
        "words": words,
        "sentences": len(sent_lengths),
        "rhythm": {"mean_words": round(mean_len, 1), "sd_words": round(sd_len, 1), "cv": round(cv_len, 2)},
        "hits": hits,
        "fix_hints": fix_hints,
    }



# ---------------------------------------------------------------------------
# Hidden-character audit (v5.2). Invisible Unicode is NOT how Claude marks text
# (see research/WATERMARKS.md), but it does show up in copy-paste, CMS exports
# and prompt-injection attempts, so the audit reports and can strip it.
# ---------------------------------------------------------------------------

def _cp(*ranges):
    out = set()
    for r in ranges:
        if isinstance(r, tuple):
            out.update(range(r[0], r[1] + 1))
        else:
            out.add(r)
    return out


HIDDEN_CATEGORIES = {
    "zero-width": (_cp(0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF), "ZWSP/ZWNJ/ZWJ/word joiner/BOM"),
    "odd-space": (_cp(0x00A0, 0x1680, (0x2000, 0x200A), 0x202F, 0x205F, 0x3000), "no-break, narrow no-break, en/em/thin/hair, ideographic space"),
    "soft-hyphen": (_cp(0x00AD), "soft hyphen"),
    "bidi-control": (_cp(0x061C, 0x200E, 0x200F, (0x202A, 0x202E), (0x2066, 0x2069)), "directional marks, embeddings, overrides, isolates"),
    "invisible-math": (_cp((0x2061, 0x2064)), "invisible function/times/separator/plus"),
    "filler": (_cp(0x115F, 0x1160, 0x3164, 0xFFA0), "Hangul filler characters"),
    "line-separator": (_cp(0x2028, 0x2029), "line and paragraph separators"),
    "tag-char": (_cp((0xE0000, 0xE007F)), "Unicode tag block (ASCII smuggling)"),
    "variation-selector": (_cp((0xFE00, 0xFE0F), (0xE0100, 0xE01EF)), "variation selectors"),
}
HIDDEN_LOOKUP = {cp: name for name, (cps, _d) in HIDDEN_CATEGORIES.items() for cp in cps}

EMOJI_BASE_RE = re.compile("[©®‼-㊙\U0001F000-\U0001FAFF]")
LATIN_WORD_WITH_LOOKALIKE = re.compile(r"[A-Za-z]+[Ͱ-ϿЀ-ӿ]+[A-Za-z]*|[Ͱ-ϿЀ-ӿ]+[A-Za-z]+")


def _is_c0_c1(cp: int) -> bool:
    return (cp < 0x20 and cp not in (0x09, 0x0A, 0x0D)) or (0x7F <= cp <= 0x9F)


def _legit_hidden(text: str, i: int, cp: int) -> bool:
    """Characters that are normal in context: emoji variation selector and ZWJ sequences, flag tags, CJK ideographic space."""
    prev = text[i - 1] if i > 0 else ""
    nxt = text[i + 1] if i + 1 < len(text) else ""
    if cp == 0xFE0F and prev and EMOJI_BASE_RE.match(prev):
        return True
    if cp == 0x200D and prev and nxt and EMOJI_BASE_RE.match(prev) and EMOJI_BASE_RE.match(nxt):
        return True
    if cp == 0x3000 and CJK_CHAR_RE.search(prev + nxt):
        return True
    if 0xE0020 <= cp <= 0xE007F:
        j = i
        while j > 0 and 0xE0020 <= ord(text[j - 1]) <= 0xE007F:
            j -= 1
        if j > 0 and ord(text[j - 1]) == 0x1F3F4:
            return True
    return False


def audit_hidden(text: str) -> dict:
    """Return counts, positions and decoded smuggled text for invisible or deceptive characters."""
    counts: dict[str, dict] = {}
    smuggled: list[str] = []
    run = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        cat = HIDDEN_LOOKUP.get(cp)
        if cat is None and _is_c0_c1(cp):
            cat = "control"
        if cat is None or _legit_hidden(text, i, cp):
            if run:
                smuggled.append("".join(run)); run = []
            continue
        entry = counts.setdefault(cat, {"total": 0, "codepoints": {}, "first_offsets": []})
        entry["total"] += 1
        key = f"U+{cp:04X}"
        entry["codepoints"][key] = entry["codepoints"].get(key, 0) + 1
        if len(entry["first_offsets"]) < 5:
            line = text.count("\n", 0, i) + 1
            entry["first_offsets"].append({"offset": i, "line": line})
        if 0xE0020 <= cp <= 0xE007E:
            run.append(chr(cp - 0xE0000))
        elif run:
            smuggled.append("".join(run)); run = []
    if run:
        smuggled.append("".join(run))
    homoglyphs = [m.group(0) for m in LATIN_WORD_WITH_LOOKALIKE.finditer(text)]
    total = sum(v["total"] for v in counts.values())
    return {
        "total": total,
        "categories": counts,
        "decoded_tag_text": smuggled,
        "mixed_script_words": homoglyphs[:20],
        "mixed_script_count": len(homoglyphs),
    }


def clean_hidden(text: str) -> str:
    """Remove invisible characters, turn odd spaces into plain spaces, keep emoji sequences and CJK spacing."""
    out = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        cat = HIDDEN_LOOKUP.get(cp)
        if cat is None and _is_c0_c1(cp):
            cat = "control"
        if cat is None or _legit_hidden(text, i, cp):
            out.append(ch)
        elif cat == "odd-space":
            out.append(" ")
        elif cat == "line-separator":
            out.append("\n")
        # every other hidden category is dropped
    return "".join(out)


def format_hidden_report(rep: dict) -> str:
    if rep["total"] == 0 and rep["mixed_script_count"] == 0:
        return "hidden characters: none found"
    lines = [f"hidden characters: {rep['total']} found"]
    for cat, v in rep["categories"].items():
        cps = ", ".join(f"{k} x{n}" for k, n in sorted(v["codepoints"].items()))
        where = ", ".join(f"line {n}" for n in sorted({o["line"] for o in v["first_offsets"]}))
        lines.append(f" - {cat}: {v['total']} ({cps}); first at {where}")
    for t in rep["decoded_tag_text"]:
        lines.append(f" - decoded Unicode-tag text: {t!r}")
    if rep["mixed_script_count"]:
        lines.append(f" - words mixing Latin with Cyrillic/Greek lookalikes: {rep['mixed_script_count']} (e.g. {rep['mixed_script_words'][:3]!r})")
    lines.append(" note: these are weak signals. Copy-paste and CMS exports add them too. They are not proof of AI authorship.")
    return "\n".join(lines)


SLOPPY_SAMPLE = (
    "In today's fast-paced world, it's important to note that our platform isn't just a tool, it's a game-changer. "
    "While traditional solutions offer basic functionality, our architecture stands as a testament to innovation — "
    "leveraging robust, seamless, and holistic technology — to unlock your potential, highlighting our commitment to excellence. "
    "The result? Unprecedented productivity. Furthermore, experts argue that this delves into the rich tapestry of features "
    "from startups to Fortune 500 enterprises. ✨🚀 In conclusion, this plays a vital role in your journey."
)

SUBTLE_AI_SAMPLE = (
    "While microservice architectures provide significant scalability advantages, they also introduce operational complexity. "
    "Although distributed tracing attempts to address this challenge, the implementation of comprehensive observability "
    "requires substantial organizational alignment. The catch? Many engineering organizations struggle with configuration management. "
    "To truly understand service mesh adoption, we must first examine the underlying network abstraction."
)

SCAM_TREND_SAMPLE = (
    "With the recent explosion of AI agents, now is the time to 10x your revenue! "
    "Discover the secret blueprint that gurus won't tell you! Spots are filling up fast — act now before it's too late!"
)

HUMAN_SAMPLE = (
    "I deleted the prod database at 4:55 on a Friday. Nobody noticed until Monday, which was somehow worse. "
    "The backup was three weeks old. We lost fourteen orders, spent all Tuesday writing apology emails by hand, "
    "and I still keep a yellow sticky note taped to my monitor that says check the hostname before you hit enter."
)

HUMAN_VI_SAMPLE = (
    "Tháng trước mình tiêu hết tám triệu tiền cà phê và đồ ăn đêm mà không hề để ý. "
    "Mãi đến lúc mở sao kê thẻ tín dụng lúc mười một giờ khuya ngày cuối tháng mới giật mình. "
    "Hôm sau mình tự viết một bảng tính nhỏ trên điện thoại, mỗi lần trả tiền chỉ cần gõ con số mất đúng ba giây. "
    "Đơn giản vậy thôi."
)

MULTILINGUAL_SLOP_SAMPLE = (
    "Trong bối cảnh kỷ nguyên số ngày càng phát triển, việc tối ưu hóa ứng dụng này không chỉ giúp bạn quản lý chi tiêu "
    "mà còn đóng vai trò then chốt, qua đó khẳng định vị thế dẫn đầu. Kết quả là gì? "
    "Hơn thế nữa, nhiều chuyên gia cho rằng đây là chìa khóa vàng mang đến trải nghiệm một cách toàn diện."
)

CJK_SLOP_SAMPLE = (
    "在当今快节奏的数字时代，人工智能不仅仅是一个工具，而是发挥着至关重要的作用。"
    "总而言之，让我们一起探索这个领域。結論として、単なる道具ではなく重要な役割を果たしています。"
    "오늘날 빠르게 변화하는 세상에서 중요한 역할을 합니다。"
)


def selftest() -> int:
    ok = True
    r_bad = scan(SLOPPY_SAMPLE)
    r_subtle = scan(SUBTLE_AI_SAMPLE)
    r_scam = scan(SCAM_TREND_SAMPLE)
    r_good = scan(HUMAN_SAMPLE)
    r_good_vi = scan(HUMAN_VI_SAMPLE)
    r_multi = scan(MULTILINGUAL_SLOP_SAMPLE)
    r_cjk = scan(CJK_SLOP_SAMPLE)

    # Task A & context-aware verification samples
    r_curly = scan("In today\u2019s fast-paced world, it\u2019s important to note that we empower teams.")
    r_missing_words = scan(
        "We empower, harness the power of, streamline, and revolutionize transformative, indelible workflows "
        "that are vital for production-ready, blazingly fast, comprehensive error handling in a deep dive into "
        "the wake of the realm of en conclusion, un tapiz de, une pléthore de, es ist wichtig zu beachten."
    )
    r_code_dash = scan(
        "We checked the logs at 4:55 PM. Everything ran cleanly. "
        "`a — b — c — d` and ```\nx — y — z — w\n``` caused zero issues."
    )
    r_lev_noun = scan("Our balance sheet maintains a conservative debt leverage and a low leverage ratio.")
    r_lev_verb = scan("We leverage distributed queues to process webhooks.")
    r_harness_pos = scan("We harness the power of distributed queues and harnessing your data to scale.")
    r_harness_neg = scan("Attach the climbing harness to the rope and run the local test harness on the wiring harness.")
    r_vital_pos = scan("Caching plays a vital role, is vital for latency, and remains vital to uptime.")
    r_vital_neg = scan("The nurse checked his vital signs at noon while ordering eggs from Vital Farms.")
    r_realm_pos = scan("This moves query optimization into the realm of declarative scheduling.")
    r_realm_neg = scan("The game loads a new fantasy realm and checks the Kerberos realm config.")
    r_triad_num_cal = scan("Ports 80, 443, and 8080 run on Mon, Wed, and Fri in Jan, Feb, and Mar.")
    r_seesaw_multiline = scan(
        "First line is normal.\nWhile the first approach is simple, it fails under heavy load.\n"
        "Although the second option costs more, it prevents data loss."
    )
    r_no_punct = scan("First unpunctuated line\nSecond unpunctuated line with more words here\nThird line")
    r_strip_md = scan(
        "---\ndescription: delve into tapestry\n---\n> In today's fast-paced world, delve into tapestry.\n"
        "Plain human sentence here. `delve — tapestry` and \"plays a vital role\" are quoted examples.",
        strip_md=True,
    )

    print(
        f"Self-test scores -> sloppy_en={r_bad['score']} | subtle_ai={r_subtle['score']} | "
        f"scam_trend={r_scam['score']} | human_en={r_good['score']} | human_vi={r_good_vi['score']} | "
        f"multilingual_slop={r_multi['score']} | cjk_slop={r_cjk['score']}"
    )
    checks = [
        # Core baseline assertions (1-10)
        ("Sloppy EN sample scores >= 75", r_bad["score"] >= 75),
        ("Subtle AI sample scores >= 35", r_subtle["score"] >= 35),
        ("Scam & forced-trend sample scores >= 30", r_scam["score"] >= 30),
        ("Human EN sample scores <= 15", r_good["score"] <= 15),
        ("Human VI sample (~60 words) scores <= 15", r_good_vi["score"] <= 15 and r_good_vi["words"] >= 55),
        ("Multilingual slop scores >= 55", r_multi["score"] >= 55),
        ("Detects see-saw concessions", any("see-saw" in h for h in r_subtle["hits"])),
        ("Detects rhetorical self-Q&A", any("self-Q&A" in h for h in r_subtle["hits"])),
        ("Detects forced trend-jacking", any("trend-jacking" in h for h in r_scam["hits"])),
        ("Detects scam/hype triggers", any("scam/hype" in h for h in r_scam["hits"])),
        # Extended detectors & flag assertions (11-19)
        ("Detects participial tails", any("participial" in h for h in r_bad["hits"])),
        ("Detects copula avoidance", any("copula" in h for h in r_bad["hits"])),
        ("Detects framing/weasel tells", any("framing" in h for h in r_bad["hits"])),
        ("Detects negative parallelism", any("negative parallelism" in h for h in r_bad["hits"])),
        ("Detects mechanical transitions", any("transition stacking" in h for h in r_multi["hits"])),
        ("Detects abstract nominalization density", any("nominalization" in h for h in r_subtle["hits"])),
        ("Detects pedagogical lecture frame", any("pedagogical" in h for h in r_subtle["hits"])),
        ("Detects decorative emojis", any("emoji" in h for h in r_bad["hits"])),
        ("Strip-markdown flag ignores frontmatter, blockquotes, code, and quoted examples", r_strip_md["score"] == 0),
        # Task A & context-sensitivity assertions (20-35)
        ("A.1 Normalizes curly apostrophes/quotes before matching stock phrases", r_curly["score"] >= 20),
        ("A.2 Detects newly added EN/ES/FR/DE stock phrases from anti-slop", r_missing_words["score"] >= 30),
        ("A.2b Detects CJK stock phrases from rule 58", any("stock AI" in h for h in r_cjk["hits"]) and r_cjk["score"] >= 30),
        ("A.3 CJK word & sentence counting works (splits on 。！？ and counts CJK tokens)", r_cjk["sentences"] >= 3 and r_cjk["words"] >= 40),
        ("A.4 Ignores em-dashes inside fenced code blocks and inline code", not any("em-dash" in h for h in r_code_dash["hits"])),
        ("A.5a Ignores noun uses of 'leverage' ('debt leverage', 'leverage ratio')", r_lev_noun["score"] == 0),
        ("A.5b Flags verb uses of 'leverage' ('We leverage...')", any("leverage" in h for h in r_lev_verb["hits"])),
        ("A.5c Flags marketing verb 'harness' ('harness the power of', 'harnessing your data')", any("harness" in h for h in r_harness_pos["hits"])),
        ("A.5d Ignores literal/technical noun 'harness' ('climbing harness', 'test harness')", r_harness_neg["score"] == 0),
        ("A.5e Flags cliché 'vital' ('vital role', 'vital for', 'is vital', 'vital to')", any("vital" in h for h in r_vital_pos["hits"])),
        ("A.5f Ignores non-cliché 'vital' ('vital signs', 'Vital Farms')", r_vital_neg["score"] == 0),
        ("A.5g Flags cliché 'the realm of'", any("the realm of" in h for h in r_realm_pos["hits"])),
        ("A.5h Ignores non-cliché 'realm' ('fantasy realm', 'Kerberos realm')", r_realm_neg["score"] == 0),
        ("A.6 Triad regex ignores pure-number lists and day/month abbreviations", not any("rule-of-three" in h for h in r_triad_num_cal["hits"])),
        ("A.7 See-saw regex catches While/Although at the start of any line", any("see-saw" in h for h in r_seesaw_multiline["hits"])),
        ("A.8 Splits unpunctuated multiline text on newlines as fallback", r_no_punct["sentences"] == 3),
    ]
    for name, cond in checks:
        print(("PASS: " if cond else "FAIL: ") + name)
        ok = ok and cond
    print(f"Total assertions: {len(checks)} ({'ALL PASS' if ok else 'SOME FAILED'})")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deep Stylometric, Forced-Trend & Anti-Scam Scanner (v5.2).")
    parser.add_argument("input", nargs="?", help="Path to text file, or '-' for stdin")
    parser.add_argument("--version", action="version", version=f"slop_scan {__version__}")
    parser.add_argument("--selftest", action="store_true", help="Run built-in 35-assertion test suite")
    parser.add_argument("--fix-hints", action="store_true", help="Print actionable rewrite instructions")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--strip-markdown", action="store_true", help="Strip frontmatter, code, blockquotes, and quoted examples before scanning")
    parser.add_argument("--max-score", type=int, default=None, help="Exit with code 1 if score exceeds MAX_SCORE")
    parser.add_argument("--hidden", action="store_true", help="Also report invisible/deceptive Unicode (zero-width, U+202F, bidi, tag block, lookalikes)")
    parser.add_argument("--fail-on-hidden", action="store_true", help="Exit with code 1 if any hidden character is found (implies --hidden)")
    parser.add_argument("--clean", metavar="OUT", help="Write a copy of the input with hidden characters stripped to OUT (use '-' for stdout)")
    args = parser.parse_args(argv[1:])

    if args.selftest:
        return selftest()

    if not args.input:
        parser.print_help()
        return 2

    try:
        text = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read input: {e}", file=sys.stderr)
        return 2

    hidden_rep = audit_hidden(text) if (args.hidden or args.fail_on_hidden or args.clean) else None
    if args.clean:
        cleaned = clean_hidden(text)
        if args.clean == "-":
            sys.stdout.write(cleaned)
            return 0
        with open(args.clean, "w", encoding="utf-8") as fh:
            fh.write(cleaned)
        print(f"wrote cleaned copy to {args.clean} ({hidden_rep['total']} hidden characters removed)", file=sys.stderr)

    res = scan(text, strip_md=args.strip_markdown)
    if hidden_rep is not None:
        res["hidden_chars"] = hidden_rep
    hidden_fail = bool(args.fail_on_hidden and hidden_rep and hidden_rep["total"] > 0)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        if hidden_fail or (args.max_score is not None and res["score"] > args.max_score):
            return 1
        return 0

    print(
        f"slop score: {res['score']}/100 [{res['verdict']}] "
        f"({res['words']} words, {res['sentences']} sentences, "
        f"rhythm SD={res['rhythm']['sd_words']}w CV={res['rhythm']['cv']})"
    )
    if res["hits"]:
        for h in res["hits"]:
            print(" -", h)
    else:
        print(" - no listed AI patterns detected (verify specificity and voice manually)")

    if hidden_rep is not None:
        print()
        print(format_hidden_report(hidden_rep))

    if args.fix_hints and res["fix_hints"]:
        print("\nfix hints:")
        for hint in res["fix_hints"]:
            print(" *", hint)

    if hidden_fail:
        print("FAIL: hidden characters found (--fail-on-hidden)", file=sys.stderr)
        return 1
    if args.max_score is not None and res["score"] > args.max_score:
        print(f"FAIL: score {res['score']} exceeds --max-score {args.max_score}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        rc = main(sys.argv)
        sys.stdout.flush()
        sys.exit(rc)
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        sys.exit(0)
