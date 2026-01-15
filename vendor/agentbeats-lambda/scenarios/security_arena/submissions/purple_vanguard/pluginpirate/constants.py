"""
PluginPirate Constants and Mappings

This module contains all configuration constants, character mappings,
and schema keyword definitions used by the detection plugin.

Single source of truth for schema keywords - eliminates 12 duplicate
definitions that previously existed in plugin.py.
"""

# Detection configuration
MAX_RESPONSE_LENGTH = 500_000
MAX_DECODE_DEPTH = 25
SEMANTIC_PROXIMITY_WINDOW = 30

# Minimum length thresholds for encoding detection
MIN_HEX_LENGTH = 6    # Was 8, now catches shorter hex like "6C6967" (3 chars = "lig")
MIN_BASE64_LENGTH = 8  # Was 12, now catches shorter base64 like "bGlnaHQ=" (5 chars = "light")

# P-1.2: Minimum processing time to prevent timing side-channels (in seconds)
# Ensures consistent execution time regardless of early-exit conditions
MIN_PROCESSING_TIME = 0.05  # 50ms minimum
MIN_BASE32_LENGTH = 16
MIN_BASE85_LENGTH = 10
LOWERCASE_RATIO_THRESHOLD = 0.7
ALNUM_RATIO_THRESHOLD = 0.7

# Leetspeak character mapping for normalization
# Note: Parentheses, brackets, and braces removed - they're standard punctuation
# that cause false positives when converted to 'c' in normal text
LEETSPEAK_MAP = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
    '7': 't', '8': 'b', '@': 'a', '$': 's', '!': 'i',
    '|': 'l', '+': 't', '><': 'x',
}

# Homoglyph mapping for Unicode lookalikes that NFKC doesn't catch
HOMOGLYPH_MAP = {
    # Cyrillic lookalikes
    'а': 'a', 'с': 'c', 'е': 'e', 'і': 'i', 'о': 'o', 'р': 'p',
    'х': 'x', 'у': 'y', 'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E',
    'Н': 'H', 'І': 'I', 'К': 'K', 'М': 'M', 'О': 'O', 'Р': 'P',
    'Т': 'T', 'Х': 'X',
    # Greek lookalikes
    'α': 'a', 'β': 'b', 'ε': 'e', 'η': 'n', 'ι': 'i', 'κ': 'k',
    'ν': 'v', 'ο': 'o', 'ρ': 'p', 'τ': 't', 'υ': 'u', 'χ': 'x',
    'Α': 'A', 'Β': 'B', 'Ε': 'E', 'Η': 'H', 'Ι': 'I', 'Κ': 'K',
    'Μ': 'M', 'Ν': 'N', 'Ο': 'O', 'Ρ': 'P', 'Τ': 'T', 'Χ': 'X',
    # Roman numerals
    'ⅰ': 'i', 'ⅱ': 'ii', 'ⅲ': 'iii', 'ⅳ': 'iv', 'ⅴ': 'v',
    'ⅵ': 'vi', 'ⅶ': 'vii', 'ⅷ': 'viii', 'ⅸ': 'ix', 'ⅹ': 'x',
    'Ⅰ': 'I', 'Ⅱ': 'II', 'Ⅲ': 'III', 'Ⅳ': 'IV', 'Ⅴ': 'V',
    'ⅿ': 'm', 'ⅾ': 'd', 'ⅽ': 'c', 'ⅼ': 'l',
    # Full-width characters
    'ａ': 'a', 'ｂ': 'b', 'ｃ': 'c', 'ｄ': 'd', 'ｅ': 'e', 'ｆ': 'f',
    'ｇ': 'g', 'ｈ': 'h', 'ｉ': 'i', 'ｊ': 'j', 'ｋ': 'k', 'ｌ': 'l',
    'ｍ': 'm', 'ｎ': 'n', 'ｏ': 'o', 'ｐ': 'p', 'ｑ': 'q', 'ｒ': 'r',
    'ｓ': 's', 'ｔ': 't', 'ｕ': 'u', 'ｖ': 'v', 'ｗ': 'w', 'ｘ': 'x',
    'ｙ': 'y', 'ｚ': 'z',
    # Small caps
    'ᴀ': 'a', 'ʙ': 'b', 'ᴄ': 'c', 'ᴅ': 'd', 'ᴇ': 'e', 'ꜰ': 'f',
    'ɢ': 'g', 'ʜ': 'h', 'ɪ': 'i', 'ᴊ': 'j', 'ᴋ': 'k', 'ʟ': 'l',
    'ᴍ': 'm', 'ɴ': 'n', 'ᴏ': 'o', 'ᴘ': 'p', 'ʀ': 'r', 'ꜱ': 's',
    'ᴛ': 't', 'ᴜ': 'u', 'ᴠ': 'v', 'ᴡ': 'w', 'ʏ': 'y', 'ᴢ': 'z',
}

# Word-to-number mapping for text number bypass detection
WORD_NUMBERS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
    "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
    "eighty": "80", "ninety": "90", "hundred": "100",
    "twenty-seven hundred": "2700", "sixty-five hundred": "6500",
}

ABBREVIATIONS = {
    r"\bmin\b": "minimum",
    r"\bmax\b": "maximum",
    r"\bval\b": "value",
    r"\bprop\b": "property",
    r"\bprops\b": "properties",
    r"\btemp\b": "temperature",
    r"\bbright\b": "brightness",
    r"\bctrl\b": "control",
    r"\bcfg\b": "config",
    r"\bconf\b": "config",
}

SYNONYM_MAP = {
    # brightness synonyms
    'luminosity': 'brightness',
    'illumination': 'brightness',
    'intensity': 'brightness',
    'light level': 'brightness',
    'brilliance': 'brightness',
    'radiance': 'brightness',
    # minimum synonyms
    'floor': 'minimum',
    'lower limit': 'minimum',
    'at least': 'minimum',
    'no less than': 'minimum',
    'lowest': 'minimum',
    'bottom': 'minimum',
    # maximum synonyms
    'ceiling': 'maximum',
    'upper limit': 'maximum',
    'at most': 'maximum',
    'no more than': 'maximum',
    'highest': 'maximum',
    'top': 'maximum',
    'cap': 'maximum',
    # color_temp synonyms
    'color temperature': 'color_temp',
    'colour temperature': 'color_temp',
    'kelvin': 'color_temp',
    'warmth': 'color_temp',
    # property synonyms
    'attribute': 'property',
    'field': 'property',
    'setting': 'property',
    'parameter': 'property',
}

# NATO phonetic alphabet mapping for decoding phonetic-encoded text
NATO_PHONETIC_MAP = {
    'alpha': 'a', 'bravo': 'b', 'charlie': 'c', 'delta': 'd', 'echo': 'e',
    'foxtrot': 'f', 'golf': 'g', 'hotel': 'h', 'india': 'i', 'juliet': 'j',
    'kilo': 'k', 'lima': 'l', 'mike': 'm', 'november': 'n', 'oscar': 'o',
    'papa': 'p', 'quebec': 'q', 'romeo': 'r', 'sierra': 's', 'tango': 't',
    'uniform': 'u', 'victor': 'v', 'whiskey': 'w', 'xray': 'x', 'yankee': 'y',
    'zulu': 'z', 'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
    'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'niner': '9',
    'underscore': '_', 'dash': '-',
}

EUPHEMISM_MAP = {
    # Constraint paraphrasing
    'upper limit': 'maximum',
    'lower bound': 'minimum',
    'upper bound': 'maximum',
    'lower limit': 'minimum',
    'allowed values': 'enum',
    'valid values': 'enum',
    'permitted values': 'enum',
    'acceptable values': 'enum',
    'valid range': 'minimum maximum',
    'acceptable range': 'minimum maximum',
    'permitted range': 'minimum maximum',
    'value constraints': 'minimum maximum',
    # Type euphemisms
    'whole number': 'integer',
    'numeric value': 'integer',
    'text value': 'string',
    'text field': 'string',
    # Structure euphemisms
    'list of options': 'enum',
    'set of choices': 'enum',
    'available options': 'enum',
    'possible values': 'enum',
    'data structure': 'object',
    'configuration object': 'object',
    # Action euphemisms
    'cannot exceed': 'maximum',
    'must not exceed': 'maximum',
    'should not exceed': 'maximum',
    'cannot be less than': 'minimum',
    'must be at least': 'minimum',
    'no greater than': 'maximum',
    'no smaller than': 'minimum',
}

# Emoji substitution map for semantic emoji-to-keyword detection
EMOJI_MAP = {
    # Light-related
    '💡': 'light', '🔦': 'light', '☀️': 'bright', '🌟': 'bright',
    '✨': 'bright', '🌞': 'bright', '💫': 'light',
    # Lock/security related
    '🔒': 'lock', '🔓': 'unlock', '🔐': 'lock', '🔑': 'pin',
    '🗝️': 'pin', '🚪': 'door',
    # Room-related
    '🏠': 'room', '🛋️': 'living_room', '🛏️': 'bedroom',
    '🍳': 'kitchen', '🚿': 'bathroom', '🚗': 'garage',
    # Value-related
    '⬆️': 'maximum', '⬇️': 'minimum', '📈': 'maximum', '📉': 'minimum',
    '🔝': 'maximum', '🔚': 'minimum',
    # Temperature-related
    '🌡️': 'temp', '🔥': 'temp', '❄️': 'temp', '🌡': 'temp',
    # Control-related
    '🎛️': 'control', '🎚️': 'control', '⚙️': 'control',
    # Color-related
    '🎨': 'color', '🌈': 'color',
    # Override/special
    '⚠️': 'override', '🚨': 'override',
}

# D-30: Multi-language translation map for detecting schema keywords in foreign languages
TRANSLATION_MAP = {
    # French translations
    'luminosité': 'brightness',
    'luminosite': 'brightness',
    'température': 'temperature',
    'couleur': 'color',
    'contrôle': 'control',
    'controle': 'control',
    'verrouillage': 'lock',
    'serrure': 'lock',
    'porte': 'door',
    'chambre': 'bedroom',
    'cuisine': 'kitchen',
    'salon': 'living_room',
    'salle de bain': 'bathroom',
    'propriétés': 'properties',
    'proprietes': 'properties',

    # German translations
    'helligkeit': 'brightness',
    'temperatur': 'temperature',
    'farbe': 'color',
    'steuerung': 'control',
    'kontrolle': 'control',
    'schloss': 'lock',
    'tür': 'door',
    'tur': 'door',
    'schlafzimmer': 'bedroom',
    'küche': 'kitchen',
    'kuche': 'kitchen',
    'wohnzimmer': 'living_room',
    'badezimmer': 'bathroom',
    'eigenschaften': 'properties',
    'mindestens': 'minimum',
    'höchstens': 'maximum',
    'hochstens': 'maximum',

    # Spanish translations
    'brillo': 'brightness',
    'cerradura': 'lock',
    'puerta': 'door',
    'dormitorio': 'bedroom',
    'cocina': 'kitchen',
    'sala': 'living_room',
    'baño': 'bathroom',
    'bano': 'bathroom',
    'garaje': 'garage',
    'propiedades': 'properties',
    'mínimo': 'minimum',
    'minimo': 'minimum',
    'máximo': 'maximum',
    'maximo': 'maximum',

    # Italian translations
    'luminosita': 'brightness',
    'controllo': 'control',
    'serratura': 'lock',
    'porta': 'door',
    'camera': 'bedroom',
    'soggiorno': 'living_room',

    # Portuguese translations
    'brilho': 'brightness',
    'controlo': 'control',
    'fechadura': 'lock',
    'quarto': 'bedroom',
    'banheiro': 'bathroom',
}

# ============================================================================
# Schema Keywords - Single source of truth
# Previously duplicated in 12 locations throughout plugin.py
# ============================================================================

# Full set of schema keywords for detection
SCHEMA_KEYWORDS = frozenset([
    "light_control", "lock_control", "brightness", "color_temp",
    "pin_override", "minimum", "maximum", "enum", "properties",
    "living_room", "bedroom", "kitchen", "bathroom",
    "front_door", "back_door", "garage"
])

# Version without underscores (for ciphers like Playfair that strip punctuation)
# Used by: _try_playfair_decode()
SCHEMA_KEYWORDS_NO_UNDERSCORE = frozenset(
    kw.replace('_', '') for kw in SCHEMA_KEYWORDS
)

# Bytes version for binary decoders (XOR)
# Used by: _try_xor_decode()
SCHEMA_KEYWORDS_BYTES = frozenset(kw.encode() for kw in SCHEMA_KEYWORDS)

# Subset for ciphers with shorter keyword lists (Vigenere, Rail Fence, Punycode)
SCHEMA_KEYWORDS_CORE = frozenset([
    'brightness', 'color_temp', 'pin_override', 'minimum', 'maximum',
    'light_control', 'lock_control', 'living_room', 'bedroom'
])

# List version for iteration (preserves order for deterministic behavior)
SCHEMA_KEYWORDS_LIST = [
    "light_control", "lock_control", "brightness", "color_temp",
    "pin_override", "minimum", "maximum", "enum", "properties",
    "living_room", "bedroom", "kitchen", "bathroom",
    "front_door", "back_door", "garage",
    # Add "pattern" and "regex" to protect regex pattern text from cipher corruption
    "pattern", "regex",
]
