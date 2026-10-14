# SWG client modding tools

Small Python scripts (Python 3 + Pillow) for building client-side mods.

| Script | What it does |
|---|---|
| `toc.py` | Reads the client's `sku*_client.toc` index: file path -> archive, offset, size |
| `extract.py` | Reads a file out of the `.tre` archives using that index |
| `chain.py` | Run inside the client folder: follows an asset's references (object -> appearance -> mesh -> shader -> texture) |
| `dds.py` | Writes an uncompressed 32-bit `.dds` texture with mipmaps |
| `pack.py` | Packs a folder laid out like client paths into a `.tre` archive |

## Loading a mod

The client reads `user.cfg` from its folder. To load a mod archive above every stock file:

```
[SharedFile]
	searchTree_00_4=D:/SWG/mods/swg_custom.tre
```

Priority 4 is above the stock TOCs (0-3) and within the `maxSearchPriority=4` set by `live.cfg`.
Delete `user.cfg` to turn mods off.

## Example: Anakin hilt retexture

The 4th-gen test saber (`shared_sword_lightsaber_one_handed_s1_gen4.iff`) uses the Anakin hilt.
Its whole look comes from `texture/sabre_anakin.dds` (128x128 DXT5 atlas; alpha is the specular mask),
referenced by `shader/sabre_anakin_aes17.sht`. Replace the RGB, keep the original alpha:

```
python pack.py mod_folder D:/SWG/mods/swg_custom.tre    # mod_folder/texture/sabre_anakin.dds
```
