# Mandarin to Mythar Semantic Mapping v0.4

**Status:** Draft for ratification  
**Evidence class:** Specified

Mandarin-to-Mythar input is semantic, not morphological: a recognized Mandarin semantic token is mapped to an ISF v0.4 root. This adapter does not claim a historical, grammatical, or genealogical relationship between Mandarin and Mythar.

| Mandarin | Gloss | Mythar root |
| --- | --- | --- |
| 光 (`guāng`) | light | `la` |
| 说 (`shuō`) | speak | `ra` |
| 神 (`shén`) | divine | `ia` |
| 门 (`mén`) | gate | `tor` |
| 力量 (`lìliàng`) | power | `ka` |
| 风 (`fēng`) | wind | `fu` |
| 存在 (`cúnzài`) | existence | `ma` |
| 集体 (`jítǐ`) | collective | `rum` |

The v0.4 adapter accepts these exact tokens with `source_language: "zh"`. Unknown Mandarin input is not guessed; it proceeds to normal Mythar diagnostics. Broader segmentation, syntax, and disambiguation require future ratification and conformance evidence.
