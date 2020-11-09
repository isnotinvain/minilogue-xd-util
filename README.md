# minilogue-xd-utils

Some utilties for working with minilogue xd patches and libraries

# Pretty print patch file
`python dump.py my_patch.mnlgxdprog`

or

`python dump.py my_lib.mnlgxdlib <patch_number>`

Where `<patch_number>` is the patch to dump, starting at 1 for the first patch

Thanks to @gekart for this gist this is based off of: 
https://gist.github.com/gekart/b187d3c16e6160571ccfcf6c597fea3f

This fork has a few updates from the original:
* Prints correct mod effects
* Prints user oscillator params 1 through 6, and handles the case where they aren't parseable / not used
* Some nicer ascii representations of sequence / motion data (needs test to confirm it's right currently)
