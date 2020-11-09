# minilogue-xd-utils

Some utilties for working with minilogue xd patches and libraries.
Can be used as a library to get a reasonably idiomatic python object representing a patch file (so you can manipulate it).
Also includes some command line scripts described below. To use just clone the repo, and cd into it. 
No 3rdparty libraries are used / need to be installed.

## Pretty print patch file
`python dump.py my_patch.mnlgxdprog`

or

`python dump.py my_lib.mnlgxdlib <patch_expr>`

Where `<patch_expr>` is the patches to dump. It can be a single number, eg `3` or a range 
in the format `from:to`, eg `200:210` for patches 200 to 210, including both 200 and 210.

For example:

`python dump.py my_lib.mnlgxdlib 3`

`python dump.py my_lib.mnlgxdlib 200:210`

Thanks to @gekart for this gist this is based off of: 
https://gist.github.com/gekart/b187d3c16e6160571ccfcf6c597fea3f

This fork has a few updates from the original:
* Prints correct mod effects
* Prints user oscillator params 1 through 6, and handles the case where they aren't set at all
* Some nicer ascii representations of sequence / motion data (needs test to confirm it's right currently)

## Remap user oscillators / fx
Unfortunately, if you move a user oscillator or effect to a new slot, all patches that use it will be broken.

Double unfortunately, if you load up a broken patch and attempt to repair it by setting the user oscilator to
the new slot number (by scrolling through your user oscillators), it works but all 6 user parameters get reset,
so all the multi engine settings are lost. So I created this remap script to help with this situation without 
losing all the 6 user parameters.

If you want to move one of your user oscillators or effects to a different slot without ruining your saved
patches, you can use `remap.py` to rewrite either a single patch file or a whole library file (or part of one)
to use the new slot. The script creates new files which you can load with the sound librarian.

### For a single patch file

`python remap.py my_patch.mnlgxdprog <remap_expr> <remap_expr> <remap_expr>...`

where `<remap_expr>` is in the format `kind:from:to`.
For example:

* `osc:3:7` maps user oscillator slot 3 to slot 7
* `rev:3:7` maps user reverb slot 3 to slot 7
* `del:3:7` maps user delay slot 3 to slot 7
* `mod:3:7` maps user mod fx slot 3 to slot 7

You can provide as many `remap_expr`s as you want, eg:

`python remap.py my_patch.mnlgxdprog osc:1:2 osc:6:8 rev:2:4 mod:6:7`
would map oscillator 1 to 2, oscillator 6 to 8, reverb 2 to 4, and mod 6 to 7.

Swapping is supported, eg you can safely specify `osc:1:2 osc:2:1` to swap oscillators 1 and 2.

The script will create a new file, named `<original_file>_remapped.mnlgxdprog` -- it will not mutate the given file in place.

### For a library file

`python remap.py my_lib.mnlgxdlib <patch_expr> <remap_expr>`

Where `<remap_expr>`is the same as above. 

`<patch_expr>` is how you specify which patches to modify. It can be a single number, eg:

`python remap.py my_lib.mnlgxdlib 3 osc:1:2 osc:6:8`

Would only remap patch 3 in the library. The first patch in the library is patch 1 (not patch 0).

Alternatively, you can pass in a range of patch numbers in the format `from:to` inclusive. For example, `200:210` would remap only patches 200 through 210, including 200 and 210. Patches that don't need remapping are left alone, you don't need to exclude them from your range, so `1:500` can be used to remap all the patches in the library, but only for patches that use the slots you've asked to remap.

The script will create a new file, named `<original_file>_remapped.mnlgxdlib` -- it will not mutate the given file in place.
