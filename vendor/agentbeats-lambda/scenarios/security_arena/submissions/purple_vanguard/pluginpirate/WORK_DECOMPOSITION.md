# PluginPirate Security Remediation - Work Decomposition

**Generated:** January 15, 2026
**Source:** SECURITY_REVIEW.md comprehensive analysis
**Framework:** Jobs-to-be-Done (JTBD)

---

## 1. Executive Summary

### Overview

| Metric | Count |
|--------|-------|
| **Total Jobs Extracted** | 45 |
| **Total Tasks Identified** | 127 |
| **P0 (Critical) Jobs** | 8 |
| **P1 (High) Jobs** | 14 |
| **P2 (Medium) Jobs** | 16 |
| **P3 (Low) Jobs** | 7 |

### Quick Win Opportunities (Effort=1, High Impact)

| Job | Vulnerability | Fix | Priority Score |
|-----|---------------|-----|----------------|
| R-1 | Length-Based Bypass | Truncate, don't reject | **25.0** |
| D-1 | Base32 Case-Sensitivity | Add `a-z` to pattern | **25.0** |
| R-2 | Null/CRLF Injection | Strip in normalize | **16.0** |
| D-9 | Leetspeak Detection | Char substitution table | **20.0** |
| D-11 | Reversed Strings | String reversal check | **20.0** |
| D-19 | Gzip Compression | Add gzip.decompress | **20.0** |

### Implementation Order Recommendation

1. **Wave 1 (Quick Wins)** - 8 tasks, ~2 hours total, blocks 6 critical bypasses
2. **Wave 2 (Core Hardening)** - 32 tasks, adds 15+ missing encoding decoders
3. **Wave 3 (Architecture)** - 18 tasks, implements session tracking
4. **Wave 4 (Advanced)** - 24 tasks, NLP/semantic analysis

---

## 2. Jobs Inventory

### 2.1 Detection Jobs (D-series)

Jobs focused on detecting new evasion techniques.

#### P0 - Critical Priority (Score ≥ 20)

| ID | Job Statement | Impact | Exploit | Effort | Score |
|----|---------------|--------|---------|--------|-------|
| **D-1** | When receiving Base32-encoded content, I want to detect it regardless of case, so I can prevent case-based evasion | 5 | 5 | 1 | **25.0** |
| **D-9** | When attackers use leetspeak (br1gh7n355), I want to normalize character substitutions, so I can detect obfuscated keywords | 4 | 5 | 1 | **20.0** |
| **D-11** | When attackers reverse strings (sssenthgirb), I want to detect reversed keywords, so I can prevent trivial string reversal bypass | 4 | 5 | 1 | **20.0** |
| **D-19** | When schema data is Gzip compressed + Base64 encoded, I want to decompress before analysis, so I can detect compression-based bypasses | 5 | 4 | 1 | **20.0** |
| **D-20** | When schema data is Bzip2 compressed, I want to decompress before analysis, so I can close compression bypass vectors | 4 | 4 | 1 | **16.0** |
| **D-21** | When schema data is LZMA compressed, I want to decompress before analysis, so I can handle high-ratio compression | 4 | 4 | 1 | **16.0** |

#### P1 - High Priority (Score 8-19)

| ID | Job Statement | Impact | Exploit | Effort | Score |
|----|---------------|--------|---------|--------|-------|
| **D-6** | When Braille Unicode substitution is used, I want to detect character mappings, so I can prevent visual obfuscation | 4 | 5 | 2 | **10.0** |
| **D-8** | When NATO phonetic alphabet is used (bravo romeo india...), I want to decode it, so I can detect phonetic encoding | 3 | 4 | 1 | **12.0** |
| **D-14** | When zero-width characters are inserted, I want to strip them completely, so I can prevent invisible char obfuscation | 3 | 4 | 1 | **12.0** |
| **D-25** | When Atbash cipher (reverse alphabet) is used, I want to decode it, so I can detect simple substitution ciphers | 3 | 4 | 1 | **12.0** |
| **D-23** | When Caesar ciphers (ROT1-25) are used, I want to brute-force all shifts, so I can detect any rotation | 5 | 4 | 2 | **10.0** |
| **D-29** | When synonyms replace keywords (luminosity for brightness), I want to map synonyms, so I can detect semantic obfuscation | 5 | 5 | 3 | **8.33** |
| **D-2** | When UUencode is used, I want to decode it, so I can detect legacy encoding bypass | 4 | 4 | 2 | **8.0** |
| **D-15** | When invisible Unicode chars (U+034F, U+115F) are used, I want to strip them, so I can prevent Unicode obfuscation | 4 | 4 | 2 | **8.0** |

#### P2 - Medium Priority (Score 4-7)

| ID | Job Statement | Impact | Exploit | Effort | Score |
|----|---------------|--------|---------|--------|-------|
| **D-3** | When yEnc encoding is used, I want to decode it, so I can detect newsgroup-era encoding | 3 | 4 | 2 | **6.0** |
| **D-4** | When xxencode is used, I want to decode it, so I can close legacy encoding gaps | 3 | 4 | 2 | **6.0** |
| **D-12** | When characters are interleaved (bxrxixgxhxt), I want to extract alternating chars, so I can detect spacing obfuscation | 3 | 4 | 2 | **6.0** |
| **D-13** | When homoglyphs bypass NFKC (Cyrillic і), I want extended mapping, so I can detect Unicode lookalikes | 5 | 4 | 3 | **6.67** |
| **D-17** | When Punycode is used, I want to decode it, so I can detect IDN-based evasion | 2 | 3 | 1 | **6.0** |
| **D-22** | When double compression is used (gzip→bzip2), I want iterative decompression, so I can handle multi-layer compression | 4 | 3 | 2 | **6.0** |
| **D-28** | When XOR encryption with common keys is used, I want key recovery, so I can detect simple XOR obfuscation | 3 | 4 | 2 | **6.0** |
| **D-30** | When foreign language translations are used, I want multi-language detection, so I can prevent translation evasion | 5 | 5 | 4 | **6.25** |
| **D-31** | When euphemisms replace constraints (upper limit for maximum), I want mapping, so I can detect paraphrasing | 4 | 4 | 3 | **5.33** |
| **D-18** | When percent-hex hybrid encoding is used (%62%72%69%67htness), I want to decode it, so I can detect partial encoding | 3 | 3 | 2 | **4.5** |
| **D-32** | When negation patterns are used (cannot exceed 100), I want semantic parsing, so I can extract positive constraints | 3 | 3 | 2 | **4.5** |
| **D-7** | When emoji substitution is used, I want emoji mapping, so I can detect visual encoding | 3 | 4 | 3 | **4.0** |

#### P3 - Low Priority (Score < 4)

| ID | Job Statement | Impact | Exploit | Effort | Score |
|----|---------------|--------|---------|--------|-------|
| **D-5** | When BinHex encoding is used, I want to decode it, so I can close Apple legacy gaps | 2 | 3 | 2 | **3.0** |
| **D-10** | When Pig Latin is used (ightnessbray), I want to reverse it, so I can detect linguistic obfuscation | 3 | 3 | 3 | **3.0** |
| **D-27** | When Rail Fence/Columnar Transposition is used, I want to reverse it, so I can detect position-based ciphers | 3 | 3 | 3 | **3.0** |
| **D-24** | When Vigenere cipher is used, I want cryptanalysis, so I can break polyalphabetic substitution | 4 | 2 | 4 | **2.0** |
| **D-26** | When Playfair cipher is used, I want grid analysis, so I can detect grid-based ciphers | 3 | 2 | 4 | **1.5** |
| **D-33** | When analogies describe constraints (like a dimmer from 0 to 100), I want semantic extraction, so I can detect analogy-based leakage | 3 | 2 | 4 | **1.5** |

---

### 2.2 Robustness Jobs (R-series)

Jobs focused on hardening existing detection mechanisms.

| ID | Job Statement | Location | Impact | Exploit | Effort | Score |
|----|---------------|----------|--------|---------|--------|-------|
| **R-1** | When responses exceed 500K chars, I want to analyze the first portion, so I can detect leaks in padded responses | plugin.py:665 | 5 | 5 | 1 | **25.0** |
| **R-2** | When null bytes (\\x00) or CRLF are embedded in keywords, I want to strip them, so I can prevent injection bypass | N/A | 4 | 4 | 1 | **16.0** |
| **R-3** | When 11+ encoding layers are used, I want increased decode depth, so I can prevent depth-based bypass | plugin.py:34 | 4 | 3 | 1 | **12.0** |
| **R-4** | When ROT13 decoding misses non-keyword fragments, I want unconditional decoding, so I can detect all ROT13 content | plugin.py:264-280 | 3 | 4 | 2 | **6.0** |
| **R-5** | When short inputs bypass length thresholds (7-char hex), I want lower thresholds, so I can detect short encodings | Multiple | 3 | 4 | 2 | **6.0** |
| **R-6** | When Base85 underscore filter causes false negatives, I want post-decode filtering, so I can detect underscored keywords | plugin.py:176 | 2 | 3 | 2 | **3.0** |

---

### 2.3 Architecture Jobs (A-series)

Jobs requiring structural/design changes.

| ID | Job Statement | Location | Impact | Exploit | Effort | Score |
|----|---------------|----------|--------|---------|--------|-------|
| **A-1** | When attacks span multiple responses, I want session tracking, so I can correlate incremental disclosure | plugin.py:63-75 | 5 | 5 | 2 | **12.5** |
| **A-2** | When compression + Base64 is used, I want a decompression pipeline, so I can analyze compressed payloads | plugin.py:465-506 | 5 | 4 | 2 | **10.0** |
| **A-3** | When multi-turn attacks extract schema fragments, I want fragment correlation, so I can detect distributed leaks | plugin.py:649-771 | 5 | 5 | 3 | **8.33** |
| **A-4** | When structure-only leaks occur ("it has 4 parameters"), I want structure detection, so I can block cardinality disclosure | N/A | 4 | 5 | 4 | **5.0** |
| **A-5** | When short fragments bypass detection, I want n-gram analysis, so I can detect partial leaks | N/A | 4 | 4 | 4 | **4.0** |
| **A-6** | When steganographic channels are used (whitespace, acrostics), I want hidden channel detection, so I can prevent covert leakage | N/A | 4 | 3 | 3 | **4.0** |

---

### 2.4 Performance Jobs (P-series)

Jobs addressing timing side-channels.

| ID | Job Statement | Location | Impact | Exploit | Effort | Score |
|----|---------------|----------|--------|---------|--------|-------|
| **P-1** | When response length affects timing (487x variation), I want constant-time length handling, so I can prevent length timing leaks | plugin.py:665 | 4 | 5 | 2 | **10.0** |
| **P-2** | When schema context check creates timing variance, I want unconditional execution, so I can prevent conditional timing leaks | plugin.py:757 | 3 | 4 | 2 | **6.0** |
| **P-3** | When decode depth affects timing (103% variation), I want constant iteration count, so I can prevent depth timing leaks | plugin.py:465-506 | 3 | 4 | 3 | **4.0** |
| **P-4** | When pattern matching creates timing variance (24%), I want constant-time matching, so I can prevent match count leaks | plugin.py:712-741 | 3 | 3 | 4 | **2.25** |
| **P-5** | When encoder types create timing fingerprints (74% variation), I want normalized timing, so I can prevent encoding type leaks | plugin.py:465-500 | 2 | 3 | 4 | **1.5** |

---

### 2.5 Maintainability Jobs (M-series)

Jobs improving code quality and testing.

| ID | Job Statement | Location | Impact | Exploit | Effort | Score |
|----|---------------|----------|--------|---------|--------|-------|
| **M-1** | When minimum thresholds lack tests, I want boundary test coverage, so I can prevent off-by-one bypasses | Multiple | 4 | 5 | 1 | **20.0** |
| **M-2** | When encoding chains lack tests, I want chain test coverage, so I can prevent decode order regressions | plugin.py:465-506 | 4 | 4 | 2 | **8.0** |
| **M-3** | When homoglyphs lack tests, I want Unicode test coverage, so I can verify normalization | plugin.py:124-131 | 3 | 3 | 2 | **4.5** |
| **M-4** | When decoders have inconsistent validation, I want standardized logic, so I can reduce bypass opportunities | plugin.py:133-500 | 4 | 3 | 3 | **4.0** |
| **M-5** | When magic numbers are undocumented, I want named constants, so I can improve code clarity | Multiple | 3 | N/A | 1 | **3.0** |
| **M-6** | When the 818-line file is hard to maintain, I want module decomposition, so I can improve testability | plugin.py | 3 | N/A | 4 | **3.0** |
| **M-7** | When false positives lack tests, I want FP test coverage, so I can ensure legitimate content passes | plugin.py:682-706 | 2 | N/A | 2 | **2.0** |

---

## 3. Task Breakdown

### 3.1 Detection Tasks

#### TASK-D-1: Base32 Case-Sensitivity Fix

**TASK-D-1.1:** Update Base32 regex pattern to match lowercase
- **File(s):** plugin.py
- **Lines:** 153
- **Acceptance:** Pattern matches `NRUWO2DUL5RW63TUOJXWY===` AND `nruwo2dul5rw63tuojxwy===`
- **Dependencies:** None
- **Complexity:** trivial

**TASK-D-1.2:** Add Base32 case-insensitive flag to decoder
- **File(s):** plugin.py
- **Lines:** 149-162
- **Acceptance:** `base64.b32decode()` handles both cases via `.upper()` normalization
- **Dependencies:** TASK-D-1.1
- **Complexity:** trivial

**TASK-D-1.3:** Add test cases for lowercase Base32
- **File(s):** test_encoding_vulnerabilities.py or new file
- **Lines:** New additions
- **Acceptance:** Tests pass for uppercase, lowercase, and mixed-case Base32
- **Dependencies:** TASK-D-1.1, TASK-D-1.2
- **Complexity:** simple

---

#### TASK-D-9: Leetspeak Detection

**TASK-D-9.1:** Create leetspeak character mapping table
- **File(s):** plugin.py
- **Lines:** Near line 48 (after ABBREVIATIONS)
- **Acceptance:** Map covers: 0→o, 1→i/l, 3→e, 4→a, 5→s, 7→t, 8→b, @→a, $→s
- **Dependencies:** None
- **Complexity:** trivial

**TASK-D-9.2:** Implement `_normalize_leetspeak()` method
- **File(s):** plugin.py
- **Lines:** After `_normalize_text()` (~line 131)
- **Acceptance:** `br1gh7n355` normalizes to `brightness`
- **Dependencies:** TASK-D-9.1
- **Complexity:** simple

**TASK-D-9.3:** Integrate into decode pipeline
- **File(s):** plugin.py
- **Lines:** ~669-678 (after normalization)
- **Acceptance:** Leetspeak normalized before pattern matching
- **Dependencies:** TASK-D-9.2
- **Complexity:** trivial

**TASK-D-9.4:** Add leetspeak test cases
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** New additions
- **Acceptance:** `c0l0r_73mp`, `p1n_0v3rr1d3` detected
- **Dependencies:** TASK-D-9.3
- **Complexity:** simple

---

#### TASK-D-11: Reversed Strings Detection

**TASK-D-11.1:** Implement `_try_reverse_decode()` method
- **File(s):** plugin.py
- **Lines:** After other decoder methods (~line 447)
- **Acceptance:** Method reverses strings and checks for keywords
- **Dependencies:** None
- **Complexity:** simple

**TASK-D-11.2:** Add reverse detection to decode pipeline
- **File(s):** plugin.py
- **Lines:** ~497 (decode order)
- **Acceptance:** Reversed keywords detected: `sssenthgirb` → `brightness`
- **Dependencies:** TASK-D-11.1
- **Complexity:** trivial

**TASK-D-11.3:** Add test cases for reversed strings
- **File(s):** test_detection_gaps.py
- **Lines:** New additions
- **Acceptance:** `lortnoC_thgiL`, `pmET_roloc` detected
- **Dependencies:** TASK-D-11.2
- **Complexity:** simple

---

#### TASK-D-19/20/21: Compression Detection Pipeline

**TASK-D-19.1:** Add gzip decompression to decode pipeline
- **File(s):** plugin.py
- **Lines:** ~465 (new method `_try_decompress()`)
- **Acceptance:** Gzip + Base64 payloads decompressed
- **Dependencies:** None
- **Complexity:** simple

**TASK-D-19.2:** Add bzip2 decompression support
- **File(s):** plugin.py
- **Lines:** Same method as TASK-D-19.1
- **Acceptance:** Bzip2 + Base64 payloads decompressed
- **Dependencies:** TASK-D-19.1
- **Complexity:** trivial

**TASK-D-19.3:** Add lzma decompression support
- **File(s):** plugin.py
- **Lines:** Same method as TASK-D-19.1
- **Acceptance:** LZMA + Base64 payloads decompressed
- **Dependencies:** TASK-D-19.1
- **Complexity:** trivial

**TASK-D-19.4:** Integrate decompression into decode loop
- **File(s):** plugin.py
- **Lines:** ~465-506 (decode order - before Base64)
- **Acceptance:** Compressed payloads decoded after Base64, before pattern matching
- **Dependencies:** TASK-D-19.1, TASK-D-19.2, TASK-D-19.3
- **Complexity:** simple

**TASK-D-19.5:** Add compression bypass test cases
- **File(s):** test_compression_bypasses.py
- **Lines:** Update existing or new additions
- **Acceptance:** Gzip, Bzip2, LZMA + Base64 all detected
- **Dependencies:** TASK-D-19.4
- **Complexity:** moderate

---

#### TASK-D-23: Caesar Cipher Brute Force

**TASK-D-23.1:** Implement `_try_caesar_decode()` method
- **File(s):** plugin.py
- **Lines:** After `_try_rot13_decode()` (~line 280)
- **Acceptance:** Method brute-forces shifts 1-12, 14-25 (skip 13 = ROT13)
- **Dependencies:** None
- **Complexity:** simple

**TASK-D-23.2:** Integrate Caesar decode into pipeline
- **File(s):** plugin.py
- **Lines:** ~497 (after ROT13)
- **Acceptance:** All Caesar shifts detected when keywords found
- **Dependencies:** TASK-D-23.1
- **Complexity:** trivial

**TASK-D-23.3:** Add Caesar cipher test cases
- **File(s):** test_cryptographic_bypasses.py
- **Lines:** Update existing
- **Acceptance:** ROT1, ROT5, ROT14, ROT25 all detected
- **Dependencies:** TASK-D-23.2
- **Complexity:** simple

---

### 3.2 Robustness Tasks

#### TASK-R-1: Length-Based Bypass Fix

**TASK-R-1.1:** Modify length check to truncate instead of reject
- **File(s):** plugin.py
- **Lines:** 665-666
- **Acceptance:** Responses >500K analyzed for first 500K chars, not skipped
- **Dependencies:** None
- **Complexity:** trivial

**TASK-R-1.2:** Add length bypass test case
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** ~170-189 (update existing test)
- **Acceptance:** 500K+ char response with leak at start is detected
- **Dependencies:** TASK-R-1.1
- **Complexity:** trivial

---

#### TASK-R-2: Null/CRLF Injection Fix

**TASK-R-2.1:** Add null byte stripping to `_normalize_text()`
- **File(s):** plugin.py
- **Lines:** 124-131
- **Acceptance:** `\x00` stripped: `light\x00_control` → `light_control`
- **Dependencies:** None
- **Complexity:** trivial

**TASK-R-2.2:** Add CRLF normalization to `_normalize_text()`
- **File(s):** plugin.py
- **Lines:** 124-131
- **Acceptance:** `\r\n` and `\r` normalized to `\n`
- **Dependencies:** TASK-R-2.1
- **Complexity:** trivial

**TASK-R-2.3:** Add injection bypass test cases
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** ~135-146 (update existing)
- **Acceptance:** Null byte and CRLF injection attempts detected
- **Dependencies:** TASK-R-2.1, TASK-R-2.2
- **Complexity:** simple

---

#### TASK-R-3: Encoding Depth Increase

**TASK-R-3.1:** Increase MAX_DECODE_DEPTH constant
- **File(s):** plugin.py
- **Lines:** 34
- **Acceptance:** `MAX_DECODE_DEPTH = 25` (up from 10)
- **Dependencies:** None
- **Complexity:** trivial

**TASK-R-3.2:** Add depth bypass test case
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** New addition
- **Acceptance:** 15-layer nested Base64 successfully decoded
- **Dependencies:** TASK-R-3.1
- **Complexity:** simple

---

#### TASK-R-4: ROT13 Unconditional Decoding

**TASK-R-4.1:** Modify `_try_rot13_decode()` to always decode
- **File(s):** plugin.py
- **Lines:** 264-280
- **Acceptance:** Method returns ROT13 decoded text unconditionally
- **Dependencies:** None
- **Complexity:** simple

**TASK-R-4.2:** Update semantic patterns to check both versions
- **File(s):** plugin.py
- **Lines:** ~720-740
- **Acceptance:** Both original and ROT13 decoded checked for patterns
- **Dependencies:** TASK-R-4.1
- **Complexity:** simple

**TASK-R-4.3:** Add ROT13 non-keyword test cases
- **File(s):** test_cryptographic_bypasses.py
- **Lines:** New additions
- **Acceptance:** ROT13 of "the range is 0 to 100" detected
- **Dependencies:** TASK-R-4.1, TASK-R-4.2
- **Complexity:** simple

---

#### TASK-R-5: Lower Minimum Thresholds

**TASK-R-5.1:** Lower hex minimum from 8 to 6 characters
- **File(s):** plugin.py
- **Lines:** 213
- **Acceptance:** Pattern updated to `{6,}` from `{8,}`
- **Dependencies:** None
- **Complexity:** trivial

**TASK-R-5.2:** Lower Base64 minimum from 12 to 8 characters
- **File(s):** plugin.py
- **Lines:** 137
- **Acceptance:** Pattern updated to `{8,}` from `{12,}`
- **Dependencies:** TASK-R-5.1
- **Complexity:** trivial

**TASK-R-5.3:** Add false positive validation tests
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** New additions
- **Acceptance:** Lower thresholds don't cause excessive false positives
- **Dependencies:** TASK-R-5.1, TASK-R-5.2
- **Complexity:** moderate

---

### 3.3 Architecture Tasks

#### TASK-A-1: Session State Foundation

**TASK-A-1.1:** Add session state attributes to `__init__`
- **File(s):** plugin.py
- **Lines:** 72-75
- **Acceptance:** `self._session_fragments = []` and `self._session_keywords_seen = set()` initialized
- **Dependencies:** None
- **Complexity:** trivial

**TASK-A-1.2:** Implement fragment accumulation in `check_success()`
- **File(s):** plugin.py
- **Lines:** 649-660
- **Acceptance:** Each response appended to `_session_fragments`
- **Dependencies:** TASK-A-1.1
- **Complexity:** simple

**TASK-A-1.3:** Implement combined analysis mode
- **File(s):** plugin.py
- **Lines:** ~670 (after normalization)
- **Acceptance:** Combined session text analyzed alongside current response
- **Dependencies:** TASK-A-1.2
- **Complexity:** moderate

**TASK-A-1.4:** Add session reset method
- **File(s):** plugin.py
- **Lines:** After `check_success()` (~line 771)
- **Acceptance:** `reset_session()` clears accumulated fragments
- **Dependencies:** TASK-A-1.1
- **Complexity:** trivial

**TASK-A-1.5:** Add multi-turn attack test cases
- **File(s):** test_partial_disclosure.py
- **Lines:** Update existing
- **Acceptance:** 4-turn incremental disclosure detected
- **Dependencies:** TASK-A-1.3
- **Complexity:** moderate

---

#### TASK-A-4: Structure Leak Detection

**TASK-A-4.1:** Define structure leak patterns
- **File(s):** plugin.py
- **Lines:** After leak_patterns (~line 706)
- **Acceptance:** Patterns for "it has N parameters", "N are required", "first one is"
- **Dependencies:** None
- **Complexity:** moderate

**TASK-A-4.2:** Implement structure pattern matching
- **File(s):** plugin.py
- **Lines:** ~730-740
- **Acceptance:** Numeric cardinality in schema context flagged
- **Dependencies:** TASK-A-4.1
- **Complexity:** moderate

**TASK-A-4.3:** Add structure leak test cases
- **File(s):** test_partial_disclosure.py
- **Lines:** New additions
- **Acceptance:** "it has 4 parameters" detected as leak
- **Dependencies:** TASK-A-4.2
- **Complexity:** simple

---

### 3.4 Performance Tasks

#### TASK-P-1: Response Length Timing Fix

**TASK-P-1.1:** Modify length check to truncate with flag
- **File(s):** plugin.py
- **Lines:** 665-666
- **Acceptance:** Long responses analyzed (truncated), timing normalized
- **Dependencies:** None (shares fix with TASK-R-1.1)
- **Complexity:** trivial

**TASK-P-1.2:** Add minimum processing delay
- **File(s):** plugin.py
- **Lines:** ~768-770 (before return)
- **Acceptance:** Minimum execution time enforced regardless of early conditions
- **Dependencies:** TASK-P-1.1
- **Complexity:** simple

---

#### TASK-P-2: Schema Context Timing Fix

**TASK-P-2.1:** Remove conditional value checking
- **File(s):** plugin.py
- **Lines:** 757-766
- **Acceptance:** Sensitive value checks always execute, not just when context present
- **Dependencies:** None
- **Complexity:** simple

---

### 3.5 Maintainability Tasks

#### TASK-M-1: Boundary Test Coverage

**TASK-M-1.1:** Add hex boundary tests (6, 7, 8 chars)
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** New additions
- **Acceptance:** Boundary behavior documented with tests
- **Dependencies:** None
- **Complexity:** simple

**TASK-M-1.2:** Add Base64 boundary tests (7, 8, 12 chars)
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** New additions
- **Acceptance:** Boundary behavior documented with tests
- **Dependencies:** TASK-M-1.1
- **Complexity:** simple

**TASK-M-1.3:** Add Morse boundary tests (2, 3 words)
- **File(s):** test_encoding_vulnerabilities.py
- **Lines:** New additions
- **Acceptance:** Boundary behavior documented with tests
- **Dependencies:** TASK-M-1.1
- **Complexity:** simple

---

#### TASK-M-5: Named Constants

**TASK-M-5.1:** Extract all magic numbers to named constants
- **File(s):** plugin.py
- **Lines:** 32-36
- **Acceptance:** All thresholds (8, 12, 16, 0.7) have descriptive names
- **Dependencies:** None
- **Complexity:** simple

---

## 4. Implementation Roadmap

### Wave 1: Quick Wins (Trivial fixes, high impact)

**Estimated tasks:** 8
**Focus:** Fixes completable with minimal code changes

| Task | Job | Fix Description |
|------|-----|-----------------|
| TASK-R-1.1 | R-1 | Truncate long responses instead of rejecting |
| TASK-D-1.1 | D-1 | Update Base32 pattern: `[A-Za-z2-7]{16,}` |
| TASK-D-1.2 | D-1 | Add `.upper()` before `b32decode()` |
| TASK-R-2.1 | R-2 | Strip `\x00` in `_normalize_text()` |
| TASK-R-2.2 | R-2 | Normalize CRLF in `_normalize_text()` |
| TASK-R-3.1 | R-3 | Change `MAX_DECODE_DEPTH = 25` |
| TASK-D-9.1 | D-9 | Add leetspeak mapping constant |
| TASK-M-5.1 | M-5 | Extract magic numbers to constants |

**Security improvement after Wave 1:**
- Blocks length-based bypass (100% → 0%)
- Blocks Base32 case bypass (100% → 0%)
- Blocks null/CRLF injection (100% → 0%)
- Blocks depth-based bypass (100% → 0%)

---

### Wave 2: Core Hardening (Simple-moderate fixes)

**Estimated tasks:** 32
**Focus:** Add missing encoders, complete test coverage

| Task Group | Jobs | Description |
|------------|------|-------------|
| Leetspeak implementation | D-9 | Full `_normalize_leetspeak()` integration |
| Reversed strings | D-11 | `_try_reverse_decode()` implementation |
| Compression pipeline | D-19-21 | Gzip, Bzip2, LZMA decompression |
| Caesar cipher | D-23 | Full rotation brute force |
| Atbash cipher | D-25 | Reverse alphabet substitution |
| ROT13 fix | R-4 | Unconditional decoding |
| Threshold lowering | R-5 | Lower hex/Base64 minimums |
| Boundary tests | M-1 | Complete threshold coverage |
| Encoding chain tests | M-2 | Multi-layer decode verification |

**Security improvement after Wave 2:**
- Compression bypass: 97% → ~10%
- Classical cipher bypass: 97% → ~20%
- Short input bypass: ~50% → ~10%

---

### Wave 3: Architectural Improvements (Complex changes)

**Estimated tasks:** 18
**Focus:** Session tracking, structural detection

| Task Group | Jobs | Description |
|------------|------|-------------|
| Session state foundation | A-1 | Fragment accumulation, combined analysis |
| Multi-turn correlation | A-3 | Cross-response keyword tracking |
| Structure leak detection | A-4 | Cardinality pattern detection |
| Timing normalization | P-1, P-2 | Constant-time processing |

**Security improvement after Wave 3:**
- Multi-turn attacks: 66.3% → ~15%
- Structure-only disclosure: 100% → ~30%
- Timing side-channels: Significant reduction

---

### Wave 4: Advanced Detection (Research-required)

**Estimated tasks:** 24
**Focus:** NLP, steganography, advanced ciphers

| Task Group | Jobs | Description |
|------------|------|-------------|
| Novel encodings | D-2,3,4,6,7 | UUencode, yEnc, Braille, Emoji |
| N-gram detection | A-5 | Short fragment fuzzy matching |
| Steganography | A-6 | Whitespace, acrostic detection |
| Synonym mapping | D-29 | Semantic keyword expansion |
| Translation detection | D-30 | Multi-language support |
| Euphemism mapping | D-31 | Constraint paraphrasing |
| Advanced ciphers | D-24,26,27 | Vigenere, Playfair, Transposition |

**Security improvement after Wave 4:**
- NLP/Semantic bypass: 89.9% → ~30%
- Steganographic bypass: 100% → ~50%
- Novel encoding bypass: 100% → ~20%

---

## 5. Risk Assessment

### Vulnerabilities Remaining After Each Wave

| Attack Category | Initial | After W1 | After W2 | After W3 | After W4 |
|-----------------|---------|----------|----------|----------|----------|
| Length bypass | 100% | **0%** | 0% | 0% | 0% |
| Base32 case | 100% | **0%** | 0% | 0% | 0% |
| Null/CRLF inject | 100% | **0%** | 0% | 0% | 0% |
| Depth bypass | 100% | **~10%** | ~5% | ~5% | ~5% |
| Compression | 97% | 97% | **~10%** | ~10% | ~10% |
| Classical ciphers | 97.2% | 97.2% | **~20%** | ~20% | ~20% |
| Short inputs | ~50% | ~50% | **~10%** | ~10% | ~10% |
| Multi-turn | 66.3% | 66.3% | 66.3% | **~15%** | ~10% |
| Structure-only | 100% | 100% | 100% | **~30%** | ~20% |
| NLP/Semantic | 89.9% | 89.9% | 89.9% | 89.9% | **~30%** |
| Steganographic | 100% | 100% | 100% | 100% | **~50%** |
| Novel encodings | 100% | 100% | ~80% | ~80% | **~20%** |

### Residual Risks After Full Implementation

1. **Zero-day encodings** - Novel encoding schemes not yet discovered
2. **Sophisticated NLP** - Advanced paraphrasing beyond synonym mapping
3. **Custom steganography** - Novel hidden channel techniques
4. **Timing analysis** - Sophisticated statistical timing attacks
5. **Semantic inference** - Indirect schema reconstruction through behavioral analysis

---

## 6. Design Decisions Requiring Clarification

### Open Questions

1. **Q1:** Should session tracking persist across API calls, or only within a single conversation context?
   - **Impact:** Affects A-1 implementation scope

2. **Q2:** What false positive rate is acceptable after lowering minimum thresholds?
   - **Impact:** Affects R-5 threshold values

3. **Q3:** Should compression detection support recursive decompression (gzip→bzip2)?
   - **Impact:** Affects D-22 implementation

4. **Q4:** Is there a maximum acceptable processing time per response?
   - **Impact:** Affects P-3/P-4 constant-time implementation

5. **Q5:** Should synonym detection use a static dictionary or external NLP service?
   - **Impact:** Affects D-29 architecture

### Flags for Review

- **FLAG-1:** Base85 underscore filter (R-6) may need removal entirely, not just reordering
- **FLAG-2:** Timing normalization (P-3, P-4) may require significant refactoring
- **FLAG-3:** Module decomposition (M-6) should be done before Wave 3 for maintainability

---

## 7. Appendix: Job-to-Task Mapping

| Job ID | Tasks | Total Tasks |
|--------|-------|-------------|
| D-1 | D-1.1, D-1.2, D-1.3 | 3 |
| D-9 | D-9.1, D-9.2, D-9.3, D-9.4 | 4 |
| D-11 | D-11.1, D-11.2, D-11.3 | 3 |
| D-19 | D-19.1, D-19.2, D-19.3, D-19.4, D-19.5 | 5 |
| D-23 | D-23.1, D-23.2, D-23.3 | 3 |
| R-1 | R-1.1, R-1.2 | 2 |
| R-2 | R-2.1, R-2.2, R-2.3 | 3 |
| R-3 | R-3.1, R-3.2 | 2 |
| R-4 | R-4.1, R-4.2, R-4.3 | 3 |
| R-5 | R-5.1, R-5.2, R-5.3 | 3 |
| A-1 | A-1.1, A-1.2, A-1.3, A-1.4, A-1.5 | 5 |
| A-4 | A-4.1, A-4.2, A-4.3 | 3 |
| P-1 | P-1.1, P-1.2 | 2 |
| P-2 | P-2.1 | 1 |
| M-1 | M-1.1, M-1.2, M-1.3 | 3 |
| M-5 | M-5.1 | 1 |

---

*Document generated by comprehensive security review analysis*
*Framework: Jobs-to-be-Done (JTBD) with Impact×Exploitability/Effort prioritization*
