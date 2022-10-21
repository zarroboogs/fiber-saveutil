
# Persona 5 Royal PC Save Utility

A save conversion/decryption utility for P5R PC.

## Requirements

- For save conversion - **decrypted** PS4 saves. Supported versions:
  - `CUSA17416` (P5R US)
  - `CUSA17419` (P5R EU)
- For save decryption - PC saves.
- Python 3+
  - Install Python dependencies with `python -m pip install -r requirements.txt`

## Usage

### Converting PS4 Saves to PC Saves

1. Using your preferred method, dump some **decrypted** P5R saves from your PS4, e.g. using [Apollo Save Tool][1] or PS4 Save Mounter + ftp.

   You should end up with a folder structure similar to:

   ```txt
   ps4_saves/CUSA17416_DATA01/DATA.DAT
   ps4_saves/CUSA17416_DATA01/sce_sys/param.sfo

   ps4_saves/CUSA17416_DATA02/DATA.DAT
   ps4_saves/CUSA17416_DATA02/sce_sys/param.sfo

   ps4_saves/CUSA17416_DATA03/DATA.DAT
   ps4_saves/CUSA17416_DATA03/sce_sys/param.sfo

   ...

   ps4_saves/CUSA17416_DATA16/DATA.DAT
   ps4_saves/CUSA17416_DATA16/sce_sys/param.sfo

   ps4_saves/CUSA17416_SYSTEM/SYSTEM.DAT
   ps4_saves/CUSA17416_SYSTEM/sce_sys/param.sfo
   ```

2. **Backup your dumped saves**, then convert the save folder from the previous step using:

   ```txt
   python fiber-saveutil.py convert /path/to/ps4_saves/ /path/to/pc_saves/
   ```

   The result should look like the following:

   ```txt
   pc_saves/DATA01/DATA.DAT
   pc_saves/DATA02/DATA.DAT
   pc_saves/DATA03/DATA.DAT
   pc_saves/DATA04/DATA.DAT
   pc_saves/DATA05/DATA.DAT
   pc_saves/DATA06/DATA.DAT
   pc_saves/DATA07/DATA.DAT
   pc_saves/DATA08/DATA.DAT
   pc_saves/DATA09/DATA.DAT
   pc_saves/DATA10/DATA.DAT
   pc_saves/DATA11/DATA.DAT
   pc_saves/DATA12/DATA.DAT
   pc_saves/DATA13/DATA.DAT
   pc_saves/DATA14/DATA.DAT
   pc_saves/DATA15/DATA.DAT
   pc_saves/DATA16/DATA.DAT
   pc_saves/SYSTEM/SYSTEM.DAT
   ```

3. Place the converted saves in the game's save folder (e.g. `%APPDATA%/Roaming/SEGA/P5R/Steam/<steam_id>/` for the Steam version on Windows).

4. Boot the game and load your saves.

| PS4     | Switch  | PC      |
|:-------:|:-------:|:-------:|
| ![x][2] | ![x][3] | ![x][4] |

#### Conversion Notes

- Only English (US/EU) PS4 saves are currently supported.

- Conversion is one way (PS4 -> PC).

- After converting a save from PS4, you should have the following outfits in your inventory:

  ```txt
  Yumizuki High (Hero)
  Yumizuki High (Ryuji)
  Gouto Costume (Morgana)
  Ouran High (Ann)
  Yumizuki High (Yusuke)
  Ouran High (Makoto)
  Ouran High (Haru)
  Ouran High (Futaba)
  Imperial Uniform (Akechi)
  Ouran High (Kasumi)
  ```

  Equipping any one of these will result in a soft-lock since the _Raidou Kuzunoha Costume & BGM Special Set_ was cut from the PC version - you'll need to use a [mod][6] to restore them.

- Loading a save that was converted from PS4 without an associated `param.sfo` file should still work, however saves will appear like this in the load menu:

  ![x][5]

### Decrypting PC Saves

- To decrypt a PC save:

  ```txt
  fiber-saveutil.py dump --raw /path/to/encrypted/DATA.DAT`
  ```

- To encrypt a PC save:

  ```txt
  fiber-saveutil.py dump /path/to/decrypted/DATA.DAT`
  ```

- To "resign" a decrypted save (e.g. after editing), simply "decrypt" (or encrypt) the save again to generate a new save file with the correct checksums.

#### Decryption Notes

- Make sure to **backup your saves** before running the tool.
- Saves have checksums, so you have to "resign" them after editing.
- The game supports loading decrypted saves (as long as the save checksums are valid).

[1]: https://github.com/bucanero/apollo-ps4
[2]: https://cdn.discordapp.com/attachments/546718581572894730/1032667980275920896/ps4.png
[3]: https://cdn.discordapp.com/attachments/546718581572894730/1032668019471699989/ps4_to_nx.png
[4]: https://cdn.discordapp.com/attachments/546718581572894730/1032974402641477662/ps4_to_pc.png
[5]: https://cdn.discordapp.com/attachments/546718581572894730/1032668051721703454/ps4_to_nx_without_sfo.png
[6]: https://cdn.discordapp.com/attachments/546718581572894730/1032708752538882171/Fiber_Raidou_Restore.7z
