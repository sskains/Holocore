# SWG client modding tools

Small Python scripts (Python 3 + Pillow) for building client-side mods.

| Script | What it does |
|---|---|
| `toc.py` | Reads the client's `sku*_client.toc` index: file path -> archive, offset, size |
| `extract.py` | Reads a file out of the `.tre` archives using that index |
| `chain.py` | Run inside the client folder: follows an asset's references (object -> appearance -> mesh -> shader -> texture) |
| `dds.py` | Writes an uncompressed 32-bit `.dds` texture with mipmaps |
| `pack.py` | Packs a folder laid out like client paths into a `.tre` archive |
| `blade.py` | Generates the four lightsaber blade frames (`lightsaberblade_a..d.dds`) |
| `saber_fx.py` | Generates the saber hit spark and swing-trail textures |

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

## Lightsaber blade

`shader/lightsaberblade.sht` cycles `lightsaberblade_a..d` (256x64 stock) for flicker. The pixel shader
`pixel_program/e_h_lightsaberblade*.psh` computes, with additive blending:

    color = saturate(tex.rgb * crystalColor + tex.a)

so **RGB is the glow** (tinted by the crystal color from `palette/wp_lightsaber.pal`, chosen by the
`index_color_blade` variable) and **alpha is the white-hot core**. Keep these textures grayscale.
Tip is at the left of the image, hilt end at the right. Sunrider's Destiny is palette index 29.

Effects: hit sparks use `texture/pt_lightsaber_spark.dds` (via `appearance/pt_lightsaber_*.prt`);
the swing trail uses `texture/sw_light_saber_add.dds` (via `appearance/sw_light_saber_*.swh`).

## UI icons

UI images are `ImageStyle` entries in `ui/ui_styles.inc` (`Source` = texture name under `texture/`,
`SourceRect` = inclusive pixel rect). Jedi ability icons live in `Styles.Icon.jedi.*` (60 modern 48x48
icons in `ui_new_icons_temp2/3`). `icons.py` packs replacement art into a new 1024x1024 atlas
(`texture/ui_jedi_icons_hd.dds`, 128px cells, rounded-corner alpha) and rewrites the matching
ImageStyles in a copy of `ui_styles.inc`; ship both in the mod archive. `uistyles.py` parses the styles.
