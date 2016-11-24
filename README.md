This was a fun weekend project.  The idea is to produce a more rigorous and
comprehensive set of Benedict Cumberbatch-sounding names than is available
elsewhere.

The makename.py script reads the BENEDICT.txt and CUMBERBATCH.txt files to
generate random name pairs:

    $ python makename.py
    BUGABOO CADILLAC
    $ python makename.py 
    POLITIC COUNTERMAN
    $ python makename.py 
    CANDIDATE CORTISONE

You can also seed it with a string of your own to make it perform as a
consistent name generator:

    $ python makename.py "brent tubbs"
    DEMAGOGUE COUNTERPOINT
    $ python makename.py "boyd ocon"
    BODYGUARD CONTRABAND

This project was greatly aided by Carnegie Mellon's [freely available
pronunciation dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict).  It
contains lines like this:

    BENEDICT  B EH1 N AH0 D IH2 K T 
    CUMBERBATCH  K AH1 M B ER0 B AE2 CH
    SUPERCALIFRAGILISTICEXPIALIDOCIOUS  S UW2 P ER0 K AE2 L AH0 F R AE1 JH AH0 L IH2 S T IH0 K EH2 K S P IY0 AE2 L AH0 D OW1 SH AH0 S

Programmers will mainly be interested in the rank.py file, which creates the
BENEDICT.txt and CUMBERBATCH.txt files.  It reads the CMU pronunciation
dictionary, parses the entries, and scores each word by how much it sounds like
"Benedict" or "Cumberbatch".  This is done with a custom phonetic distance
function that takes breaks each word into syllables and compares those, further
breaking each syllable into it's beginning consonants (if present), main vowel,
and ending consonants (if present).  Differences increase the distance score.
Differences in the first syllable, last syllable, or number of syllables incur
extra penalties.

After ranking all words by similarity, I arbitrarily removed all words below a
minimum threshold.  I also added in a couple words that the algorithm
unfortunately missed (e.g. "bumpercar", "cuttlefish").

TODO:

- Keep fine tuning the distance function.  Make "ch" close to "sh" for example.
- Compound words!  To really be exhaustive, the script should be able to create things like "numbercrunch".

Inspiration and prior art:

- http://imgur.com/gallery/E7UKH
- http://blubberdickcumberbund.tumblr.com/
- http://benedictcumberbatchgenerator.tumblr.com/
