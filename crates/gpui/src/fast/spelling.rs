//! The system's spell checker, asked about text.
//!
//! A text field that underlines misspellings and offers corrections needs the
//! spell checker the system already has: its languages are the ones the user
//! set, and the words the user taught it are shared with every other
//! application. Upstream offers no way to reach it. The platform answers
//! through three `Platform` methods whose default, for a platform without a
//! spell checker, is [`unsupported`]: nothing is misspelled, nothing is
//! suggested, nothing is learned.

use std::ops::Range;

use crate::App;

/// What a platform without a spell checker answers: nothing.
pub(crate) fn unsupported<T: Default>(_text: &str) -> T {
    T::default()
}

impl App {
    /// Returns the UTF-8 byte ranges of the words in `text` that the system's
    /// spell checker does not know, for a text field to mark. Empty on
    /// platforms without a system spell checker (of GPUI's, only macOS has
    /// one).
    pub fn misspelled_words(&self, text: &str) -> Vec<Range<usize>> {
        self.platform.misspelled_words(text)
    }

    /// Returns the system spell checker's suggestions for `word`, best first.
    pub fn spelling_guesses(&self, word: &str) -> Vec<String> {
        self.platform.spelling_guesses(word)
    }

    /// Adds `word` to the user's dictionary, shared with the other
    /// applications that use the system's spell checker, so that it is no
    /// longer reported.
    pub fn learn_spelling(&self, word: &str) {
        self.platform.learn_spelling(word)
    }
}

#[cfg(test)]
mod tests {
    use crate::TestAppContext;

    #[crate::test]
    fn a_platform_without_a_spell_checker_finds_nothing(cx: &mut TestAppContext) {
        cx.update(|cx| {
            assert!(cx.misspelled_words("teh wrold").is_empty());
            assert!(cx.spelling_guesses("wrold").is_empty());
            cx.learn_spelling("wrold");
        });
    }
}
