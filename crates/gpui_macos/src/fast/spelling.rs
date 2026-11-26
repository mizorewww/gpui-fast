//! The system's spell checker, `NSSpellChecker`, in the language it picks
//! for the text (the user's languages, as System Settings orders them):
//! `Platform::misspelled_words`, `spelling_guesses` and `learn_spelling` on
//! macOS (`gpui::fast::spelling`).

use std::ops::Range;

use objc2_app_kit::NSSpellChecker;
use objc2_foundation::{NSInteger, NSNotFound, NSRange, NSString};

/// The UTF-8 byte ranges of the words in `text` the system does not know.
pub(crate) fn misspelled_words(text: &str) -> Vec<Range<usize>> {
    let checker = NSSpellChecker::sharedSpellChecker();
    let string = NSString::from_str(text);
    let length = string.length();
    let mut found = Vec::new();
    let mut start = 0;
    while start < length {
        // SAFETY: a null word count is allowed.
        let range = unsafe {
            checker.checkSpellingOfString_startingAt_language_wrap_inSpellDocumentWithTag_wordCount(
                &string,
                start as NSInteger,
                None,
                false,
                0,
                std::ptr::null_mut(),
            )
        };
        if range.location == NSNotFound as usize || range.length == 0 || range.location < start {
            break;
        }
        found.push(range.location..range.location + range.length);
        start = range.location + range.length;
    }
    utf16_to_utf8(text, found)
}

/// What the system suggests for `word`, best first.
pub(crate) fn spelling_guesses(word: &str) -> Vec<String> {
    let checker = NSSpellChecker::sharedSpellChecker();
    let string = NSString::from_str(word);
    let range = NSRange::new(0, string.length());
    checker
        .guessesForWordRange_inString_language_inSpellDocumentWithTag(range, &string, None, 0)
        .map(|guesses| guesses.iter().map(|guess| guess.to_string()).collect())
        .unwrap_or_default()
}

/// Adds `word` to the user's dictionary.
pub(crate) fn learn_spelling(word: &str) {
    NSSpellChecker::sharedSpellChecker().learnWord(&NSString::from_str(word));
}

/// `ranges` of UTF-16 code units in `text`, as UTF-8 byte ranges.
fn utf16_to_utf8(text: &str, ranges: Vec<Range<usize>>) -> Vec<Range<usize>> {
    let mut bytes = Vec::with_capacity(text.len() + 1);
    for (byte, char) in text.char_indices() {
        bytes.extend(std::iter::repeat_n(byte, char.len_utf16()));
    }
    bytes.push(text.len());
    let at = |unit: usize| bytes[unit.min(bytes.len() - 1)];
    ranges
        .into_iter()
        .map(|range| at(range.start)..at(range.end))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::{misspelled_words, spelling_guesses, utf16_to_utf8};

    #[test]
    fn utf16_ranges_become_byte_ranges() {
        // "é" is one UTF-16 unit and two bytes; "😀" is two units and four bytes.
        let text = "é 😀 teh";
        assert_eq!(utf16_to_utf8(text, vec![5..8]), vec![8..11]);
        assert_eq!(utf16_to_utf8(text, vec![0..1]), vec![0..2]);
    }

    #[test]
    fn misspelled_words_are_found_by_their_byte_ranges() {
        let text = "naïve wrold, café";
        assert_eq!(misspelled_words(text), vec![7..12]);
        assert!(
            spelling_guesses("wrold")
                .iter()
                .any(|guess| guess == "world")
        );
    }
}
