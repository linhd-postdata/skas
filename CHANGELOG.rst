
Changelog
=========


0.6.0 (2021-01-28)
------------------

* Option to show rhyme pattern.
* Better documentation and README
* Fixed rhyme issue when synalepha present on rhyming syllables
* Add PoS to the output.
* Added more rhyme patterns to stanzas rules, better handling of diphthongs with 'h'.
* Refactorization, typos fixed, and added more tests.

0.5.0 (2020-09-28)
------------------

Added support for the automatic detection of most Spanish stanzas:

* Cantar
* Chamberga
* Copla arte mayor
* Copla arte menor
* Copla castellana
* Copla mixta
* Copla real
* Couplet
* Cuaderna vía
* Cuarteta
* Cuarteto
* Cuarteto lira
* Décima antigua
* Endecha real
* Espinela
* Estrofa francisco de la torre
* Estrofa manriqueña
* Estrofa sáfica
* Estrofa sáfica unamuno
* Haiku
* Lira
* Novena
* Octava
* Octava real
* Octavilla
* Ovillejo
* Quinteto
* Quintilla
* Redondilla
* Romance
* Romance arte mayor
* Seguidilla
* Seguidilla compuesta
* Seguidilla gitana
* Septeto
* Septeto lira
* Septilla
* Serventesio
* Sexta rima
* Sexteto
* Sexteto lira
* Sextilla
* Silva arromanzada
* Soleá
* Tercetillo
* Terceto
* Terceto encadenado
* Terceto monorrimo

0.4.3 (2020-03-24)
------------------

* Added support for filtering consecutive liaisons and syllabification
* Added missing documentation

0.4.2 (2020-03-11)
------------------

* Added documentation

0.4.1 (2019-12-19)
------------------

* Added 'AUX' to the split_on list for spacy affixes
* Fixed syllabification exceptions, support for disabling/enabling spacy_affixes
* Fixed multiline break
* Fixed splitted verb stresses and secondary stress on '-mente' adverbs
* Fixed some issues
* Added minimum length for '-mente' adverbs

0.4.0 (2019-11-21)
------------------

* Added SpaCy Doc input support
* Add umlaut hyatus
* Added new hyatus and fixed init
* Refactoring code
* Feat/new syllabification
* Naming conventions
* Adding rhyme analaysis to scansion output
* Adding 'singleton' behaviour to load_pipeline
* Metre analysis w/ sinaeresis and synalephas
* Added new workflow for syllabification, with tests
* Post syllabification rules regexes
* Added unit tests for all functions

0.3.0 (2019-06-18)
------------------

* Added SpaCy Doc input support
* Add umlaut hyatus
* Fixed syllabyfication errors, affixes and the pipeline
* Fixed hyphenator for diphthongs with u umlaut
* Added hyphenation for explicit hyatus with umlaut vowels
* Added new hyatus and fixed __init__

0.2.0 (2019-06-14)
------------------

* Better hyphenator, and affixes and pipeline fixes

0.1.2 (2019-06-10)
------------------

* Republishing on Pypi

0.1.0 (2019-07-03)
------------------

* Project name change.

0.0.1 (2019-02-21)
------------------

* First release on PyPI.
